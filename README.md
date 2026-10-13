# usemykey.com — the MyKey product site

The public website for **MyKey**, the offline-first password vault sold by
**2351485 ALBERTA INC.** (Calgary, Alberta, Canada).

- Live: https://usemykey.com
- Product: https://github.com/nrupala/mykey (desktop engine) ·
  https://github.com/nrupala/mykey-mobile (phone / web client)
- Support: info@aimlds.org

## What this repo holds

| Path | What it is |
|---|---|
| `site/` | The site itself: plain static HTML/CSS/JS. This is the only part a content edit should touch. |
| `worker.js` | The Cloudflare Worker that serves the site (routing, headers, the APK download redirect). |
| `tools/build_deploy.py` | Build + deploy + verify tooling (see below). |
| `downloads/MyKey.apk` | The current Android build served from the Download page via `/download/MyKey.apk` (the Worker redirects to this file's raw URL). Refreshed from the mykey-mobile release artifact; the version and SHA-256 shown on the Download page must match this file. |
| `dist/` | Generated worker bundle (git-ignored; rebuilt on every deploy). |

## Pages

Home (`/`), Download (`/download`), Buy a licence (`/buy`), Recover my
licence (`/recover`), Support & FAQ (`/support`), Privacy (`/privacy`),
Terms (`/terms`), plus `llms.txt`, `robots.txt`, `sitemap.xml`, and
`/.well-known/security.txt`.

Copy rules: plain words, no jargon in the primary UI, and **only shipped
behaviour may be claimed**. When in doubt, leave it out. The Support page
mirrors the in-app canonical help text (HELP.md / FAQ.md in the desktop
repo) — keep them in step.

## Checkout state

Checkout is gated by ONE value: `checkoutLive` in `site/config.js`.
It is **false**. There is no live Paddle account for the Inc. yet, so the
Buy page honestly shows "Checkout opens at launch" and no purchase
control is presented to the public. The config carries real Paddle
**Sandbox** product/price IDs and a sandbox client token, so the full
checkout can be exercised in test mode. To open checkout at launch:
complete Paddle live seller verification, create the live prices and
client token, set `environment` to `"production"` with the live values,
and flip `checkoutLive` to `true`.

## Build

```bash
python3 tools/build_deploy.py build   # wraps site/ into dist/ worker modules
```

The bundle is sanity-checked locally before any deploy (the module
graph loads in Node and `fetch()` is exercised against every route).

## Deploy

```bash
python3 tools/build_deploy.py deploy  # build + upload worker + attach custom domains
python3 tools/build_deploy.py verify  # fetch the live pages and check content markers
```

Deployment is a Cloudflare Worker (`usemykey-site`) on the owner's
account, attached to `usemykey.com` and `www.usemykey.com` as Worker
Custom Domains (HTTPS certificates are provisioned by Cloudflare).
Auth uses the owner's connected Cloudflare credential through the
standard surrogate helper — no keys live in this repo.

## Licence

Site content © 2351485 ALBERTA INC. Tooling and Worker code are
Apache License 2.0. The MyKey product itself is proprietary-core with
an Apache 2.0 interface layer — see the product repos.
