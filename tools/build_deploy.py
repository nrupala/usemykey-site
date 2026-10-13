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

# route name -> file in site/
ASSETS = {
    "index": "index.html",
    "download": "download.html",
    "buy": "buy.html",
    "recover": "recover.html",
    "support": "support.html",
    "privacy": "privacy.html",
    "terms": "terms.html",
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
    build()
    boundary = "----mk" + uuid.uuid4().hex
    parts = []
    metadata = {"main_module": "index.js", "compatibility_date": "2025-01-01", "bindings": []}
    parts.append((None, "metadata", "application/json", json.dumps(metadata).encode()))
    for fname in sorted(os.listdir(DIST)):
        with open(os.path.join(DIST, fname), "rb") as fh:
            parts.append((fname, fname, "application/javascript", fh.read()))
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


def verify():
    checks = {
        "https://usemykey.com/": ["Your passwords. Your device. Your key.", "2351485 ALBERTA INC.", "101EEK"],
        "https://usemykey.com/download": ["Download the Android app (APK)", "d9f4750c"],
        "https://usemykey.com/buy": ["Checkout opens at launch", "Free vs licensed"],
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
            with urllib.request.urlopen(url, timeout=30) as resp:
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
