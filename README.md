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
| `downloads/MyKey-2.2.0-*.exe`, `downloads/MyKey-2.2.0-linux-x86_64.tar.gz`, `downloads/MyKey-2.2.0-SHA256SUMS.txt` | The desktop builds (Windows app + CLI, Linux bundle) and their checksums, served from the Download page by the same Worker-redirect pattern. Built from nrupala/mykey v2.2.0; unsigned — the Download page says so. Keep the versions and sizes on the page in step with these files. |
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
It is **true** (since 2026-10-19). Payments run on the company's one
Stripe account (2351485 ALBERTA INC., public name AIMLDS) — payments
were consolidated on Stripe on 2026-10-14 and Paddle is closed. The
Buy buttons link to Stripe-hosted Payment Link pages; the live
product/price/link IDs live in `site/config.js`. This site never
sees or stores card details.

## Billing flow (webhook + issuer)

1. A buyer pays on a Stripe Payment Link. Stripe redirects them
   back to `/buy?checkout=success` (licence) or `/buy?tip=thanks`.
2. Stripe calls `POST /stripe/webhook` on this Worker. The handler
   verifies Stripe's signature (Worker secrets
   `STRIPE_WEBHOOK_SECRET` for live events,
   `STRIPE_WEBHOOK_SECRET_TEST` for test events — set out of band
   via the Cloudflare secrets API, never in this repo) and records
   the order, or the refund, in the `MYKEY_ORDERS` KV namespace.
3. The issuer step — `tools/stripe_issuer.py` in the desktop repo
   (nrupala/mykey) — polls the orders, cross-checks live orders
   against Stripe's API, mints the buyer's MKLIC1 licence key
   under the company's licence authority (the private key lives
   only in its corporate custody home — never in this Worker, this
   repo, or any log), records it in the licence registry, and
   emails the key to the buyer from info@aimlds.org. Refunds mark
   the licence revoked in the registry.

Edge note: a Cloudflare configuration rule turns the Browser
Integrity Check off for `/stripe/webhook` only — the zone's UA
filter otherwise 403s machine callers before they reach the
Worker, and Stripe's signature is the endpoint's real gate.

Deploy note: `tools/build_deploy.py deploy` attaches the
`MYKEY_ORDERS` KV binding when the `MYKEY_ORDERS_KV_ID` env var is
set. Worker secrets are NOT part of the script upload — set or
rotate them through the Cloudflare secrets API for the
`usemykey-site` script.

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
