#!/usr/bin/env python3
"""Build the usemykey.com worker bundle from site/ and deploy it.

Build: wraps each file in site/ as a JS module exporting its text,
plus index.js from worker.js with the asset imports filled in.
Deploy: PUT the bundle to the Cloudflare Workers scripts API as a
multipart module upload (metadata part + one part per module),
then attach/refresh the Worker Custom Domains for usemykey.com and
www.usemykey.com.

Usage:
  python3 tools/build_deploy.py build     # writes dist/
  python3 tools/build_deploy.py deploy    # build + upload + domains
  python3 tools/build_deploy.py verify    # fetch live pages & check markers

Auth: the user-connected custom.cloudflare credential via the
skill-creator surrogate helper. No raw keys are read or printed.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
import uuid

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
DIST = os.path.join(ROOT, "dist")
ACCOUNT = "2edd59d09fd816187b47afbb9ea43af1"
ZONE = "451cba2d731b5dfa199fc7851ba4ebfc"
SCRIPT = "usemykey-site"

# SITE-INTEGRITY GUARD (added 2026-10-21): the deploy subcommand pushes
# straight to Cloudflare, bypassing the signed wrapper, so it refuses to
# run without an ACTIVE declaration for the usemykey-site scope, and
# certifies the live artifact after a successful deploy. (build/verify do
# not deploy and are not guarded.) Declare first:
#   python3 ~/workspace/site-integrity/declare.py add usemykey-site --hours 2 --note "<what>"
# After the deploy the script certifies via the signing service; then close:
#   python3 ~/workspace/site-integrity/declare.py close usemykey-site
import datetime as _si_dt, json as _si_json, subprocess as _si_sp, sys as _si_sys
def _si_guard(_scopes):
    try:
        _decls = _si_json.load(open('/home/hatch/workspace/site-integrity/declarations.json'))
    except Exception as _e:
        print('GUARD: cannot read declarations.json:', _e); _si_sys.exit(1)
    _now = _si_dt.datetime.now(_si_dt.timezone.utc)
    def _ts(_s): return _si_dt.datetime.fromisoformat(_s.replace('Z', '+00:00'))
    for _scope in _scopes:
        _act = [d for d in _decls if d.get('scope') == _scope and not d.get('closed_at') and _ts(d['expires_at']) > _now]
        if not _act:
            print('GUARD: no ACTIVE site-integrity declaration for scope', _scope)
            print('Run: python3 ~/workspace/site-integrity/declare.py add %s --hours 2 --note "<what>"' % _scope)
            _si_sys.exit(1)
    print('site-integrity declaration active for', ', '.join(_scopes), '- proceeding')
def _si_certify(_scope):
    _cmd = [_si_sys.executable, '/home/hatch/workspace/site-integrity/deploy_signed_client.py', _scope,
            '--surface', 'vm', '--token-file', '/home/hatch/workspace/site-integrity/.sign_token']
    _r = _si_sp.run(_cmd, capture_output=True, text=True)
    print((_r.stdout or '').strip())
    if _r.returncode != 0:
        print('CERTIFY FAILED (exit %s): %s' % (_r.returncode, (_r.stderr or '').strip()[:400]))
        print('Deploy is live but UNCERTIFIED - certify manually, then close the declaration.')
    else:
        print('Reminder: python3 ~/workspace/site-integrity/declare.py close', _scope)

# route name -> file in site/
ASSETS = {
    "index": "index.html",
    "download": "download.html",
    "buy": "buy.html",
    "recover": "recover.html",
    "support": "support.html",
    "privacy": "privacy.html",
    "terms": "terms.html",
    "releases": "releases.html",
    "styles": "styles.css",
    "config": "config.js",
    "checkout": "checkout.js",
    "favicon": "favicon.svg",
    "robots": "robots.txt",
    "sitemap": "sitemap.xml",
    "llms": "llms.txt",
    "security": "security.txt",
    "404": "404.html",
}


def build():
    os.makedirs(DIST, exist_ok=True)
    for f in os.listdir(DIST):
        os.remove(os.path.join(DIST, f))
    imports = []
    lines = ["const ASSETS = {"]
    for name, fname in ASSETS.items():
        with open(os.path.join(SITE, fname), "r", encoding="utf-8") as fh:
            text = fh.read()
        mod = f"asset_{name}.js"
        with open(os.path.join(DIST, mod), "w", encoding="utf-8") as fh:
            fh.write("export default " + json.dumps(text) + ";\n")
        imports.append(f'import a_{name} from "./{mod}";')
        lines.append(f'  "{name}": a_{name},')
    lines.append("};")
    with open(os.path.join(ROOT, "worker.js"), "r", encoding="utf-8") as fh:
        worker = fh.read()
    worker = worker.replace("//__ASSET_IMPORTS__", "\n".join(imports) + "\n\n" + "\n".join(lines))
    with open(os.path.join(DIST, "index.js"), "w", encoding="utf-8") as fh:
        fh.write(worker)
    print(f"built {len(ASSETS)} assets -> {DIST}")


def cf(method, path, data=None, headers=None):
    req = urllib.request.Request(
        "https://api.cloudflare.com" + path, method=method, data=data,
        headers=headers or {})
    add_surrogate_to_request(req, "custom.cloudflare", allowed_hosts=["api.cloudflare.com"])
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, read_json_response(resp)
    except urllib.error.HTTPError as e:
        return e.code, {"errors": e.read()[:800].decode("utf-8", "replace")}


def deploy():
    _si_guard([SCRIPT])
    build()
    boundary = "----mk" + uuid.uuid4().hex
    parts = []
    # The Stripe webhook handler needs the MYKEY_ORDERS KV binding.
    # Its namespace id is passed via the MYKEY_ORDERS_KV_ID env var
    # (an identifier, not a secret). The webhook's Stripe signing
    # secrets (STRIPE_WEBHOOK_SECRET / STRIPE_WEBHOOK_SECRET_TEST)
    # are Worker secrets set out of band via the secrets API —
    # script uploads do not carry them and must never contain them.
    bindings = []
    kv_id = os.environ.get("MYKEY_ORDERS_KV_ID")
    if kv_id:
        bindings.append({"type": "kv_namespace", "name": "MYKEY_ORDERS",
                         "namespace_id": kv_id})
    else:
        print("WARNING: MYKEY_ORDERS_KV_ID not set — deploying WITHOUT "
              "the orders binding; /stripe/webhook will answer 500 "
              "until the binding exists")
    metadata = {"main_module": "index.js", "compatibility_date": "2025-01-01",
                "bindings": bindings}
    parts.append((None, "metadata", "application/json", json.dumps(metadata).encode()))
    for fname in sorted(os.listdir(DIST)):
        with open(os.path.join(DIST, fname), "rb") as fh:
            parts.append((fname, fname, "application/javascript+module", fh.read()))
    body = b""
    for filename, name, ctype, data in parts:
        body += f"--{boundary}\r\n".encode()
        disp = f'Content-Disposition: form-data; name="{name}"'
        if filename:
            disp += f'; filename="{filename}"'
        body += disp.encode() + b"\r\n"
        body += f"Content-Type: {ctype}\r\n\r\n".encode()
        body += data + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    st, resp = cf("PUT", f"/client/v4/accounts/{ACCOUNT}/workers/scripts/{SCRIPT}",
                  data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    print("script upload:", st, str(resp)[:300])
    if st != 200:
        sys.exit(1)
    for host in ("usemykey.com", "www.usemykey.com"):
        st, resp = cf("PUT", f"/client/v4/accounts/{ACCOUNT}/workers/domains",
                      data=json.dumps({"hostname": host, "service": SCRIPT,
                                       "environment": "production", "zone_id": ZONE}).encode(),
                      headers={"Content-Type": "application/json"})
        print(f"domain {host}:", st, str(resp)[:300])
    _si_certify(SCRIPT)


def verify():
    checks = {
        "https://usemykey.com/": ["Your passwords. Your device. Your key.", "2351485 ALBERTA INC.", "101EEK", "Passkeys, kept in your vault", "Fill logins in your browser", "Payments by Stripe"],
        "https://usemykey.com/download": ["Download the Android app (APK)", "13ec2578", "MyKey-2.2.0-windows-x86_64.exe", "Browser extension"],
        "https://usemykey.com/buy": ["Free vs licensed", "US$49 suggested (pay what you want, US$29+)", "processed by Stripe", "Buying, in plain terms"],
        "https://usemykey.com/releases": ["Checkout opens", "Testing record", "282 passed, 1 skipped"],
        "https://usemykey.com/config.js": ["checkoutLive: true", "buy.stripe.com/3cIfZh1m2bEI3mD32C9Zm06", "price_1USH6BEAiA4GKFhA9scCt7HO"],
        "https://usemykey.com/recover": ["Recover my licence", "date of birth"],
        "https://usemykey.com/support": ["I forgot my master password"],
        "https://usemykey.com/privacy": ["We collect nothing"],
        "https://usemykey.com/terms": ["Calgary, Alberta"],
        "https://usemykey.com/llms.txt": ["MyKey is an offline-first password vault"],
        "https://usemykey.com/robots.txt": ["Sitemap: https://usemykey.com/sitemap.xml"],
        "https://usemykey.com/.well-known/security.txt": ["info@aimlds.org"],
    }
    ok = True
    for url, markers in checks.items():
        try:
            # Cloudflare bot-filters the default urllib user agent
            # (403 on every page) — send a browser UA so verify
            # measures the pages, not the filter.
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/126.0 Safari/537.36"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8", "replace")
                status = resp.status
        except Exception as e:  # noqa: BLE001
            print(f"FAIL {url}: {e}")
            ok = False
            continue
        missing = [m for m in markers if m not in body]
        print(("OK  " if status == 200 and not missing else "FAIL"), url, status,
              ("missing: " + str(missing)) if missing else "")
        ok = ok and status == 200 and not missing
    # try-my-key redirect
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a):
            return None
    try:
        urllib.request.build_opener(NoRedirect).open("https://trymykey.com/some/path?x=1", timeout=30)
        print("FAIL trymykey.com: no redirect")
        ok = False
    except urllib.error.HTTPError as e:
        loc = e.headers.get("Location", "")
        print(("OK  " if e.code in (301, 302, 307, 308) and "usemykey.com" in loc else "FAIL"),
              "trymykey.com redirect", e.code, loc)
        ok = ok and "usemykey.com" in loc
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    {"build": build, "deploy": deploy, "verify": verify}[cmd]()
