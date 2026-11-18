# Codetopo Profile — usemykey.com (MyKey product site) (nrupala/usemykey-site)

**What this is.** The agent-facing map of this repository, generated with
Codetopo 0.9.1 (local engine, `~/.cargo/bin/codetopo`) so an arriving agent
can see the machine — topology, trust boundaries, money surface — before it
submits or changes anything. Read this first; the graph snapshot beside it
(`snapshot.json`, `stats.json`) is the measured evidence.

- **Repo:** nrupala/usemykey-site
- **Commit profiled:** `718f68687395db859d25ffd283115445367aaab2` (main)
- **Engine:** codetopo 0.9.1 · index run 2026-11-18
- **Graph:** 7 files walked · 0 failed · 150 nodes · 246 edges · audit chain valid (3 entries, head `cf6a49ff…bd91e`)
- **Nodes by kind:** class 1 · doc 3 · external 104 · file 7 · function 14 · method 1 · module 7 · package 1 · variable 12
- **Edges by kind:** calls 127 · contains 45 · defines 1 · imports 9 · reads 63 · writes 1

## Coverage honesty

Codetopo extracts Rust, TypeScript/JavaScript and Python, plus Markdown
as Doc nodes. The graph walks 7 files: `worker.js`,
`site/checkout.js`, `site/config.js` and `tools/build_deploy.py` at
symbol level, plus docs. The 3 Markdown files are indexed as Doc
nodes only. **Not covered:** the 9 HTML pages and CSS under `site/`
(the site's actual content) are not parsed into the graph — read
them directly. The downloads (APK, Windows `.exe` builds, Linux
tarball, checksums) are binary release artifacts, not code. Repo
size (65M) is dominated by those binaries.

## Topology

The public product site for MyKey, the offline-first password
vault sold by 2351485 ALBERTA INC. (README; live at usemykey.com):

- `site/` — plain static HTML/CSS/JS: Home (`/`), Download
  (`/download`), Buy a licence (`/buy`), Recover my licence
  (`/recover`), Support & FAQ, Privacy, Terms, plus `llms.txt`,
  `robots.txt`, `sitemap.xml`, `/.well-known/security.txt`.
  `site/config.js` holds the live product/price/Payment-Link
  configuration and the single `checkoutLive` gate value;
  `site/checkout.js` is the buy-page logic.
- `worker.js` — the Cloudflare Worker serving the site (routing,
  headers, APK/desktop download redirects to the `downloads/`
  artifacts) AND the Stripe webhook endpoint
  `POST /stripe/webhook` (see Money surface), recording orders in
  the `MYKEY_ORDERS` KV namespace.
- `tools/build_deploy.py` — build + deploy + verify tooling for the
  site/Worker.
- Licence issuance itself (minting + emailing the MKLIC1 key) is
  NOT here: it is `tools/stripe_issuer.py` in the desktop repo
  `nrupala/mykey`, polling the orders this Worker records.

## Trust boundaries

- **Webhook signature verification is the trust boundary:**
  `/stripe/webhook` verifies Stripe's signature against the Worker
  secret NAMES `STRIPE_WEBHOOK_SECRET` (live events) /
  `STRIPE_WEBHOOK_SECRET_TEST` (test events) — both set out of band
  via the Cloudflare secrets API, never in this repo (`worker.js`
  L38–44, L151–154) — and refuses as "webhook not configured" (500)
  when unset. Orders are idempotently keyed, with a
  payment-intent → order index (`pi:<id>`) as a second guard
  against duplicate/charge-only events (Worker comments L60–63).
- **Licence private key never enters this surface:** the signing
  key lives only in its corporate custody home — "never in this
  Worker, this repo, or any log" (README billing flow).
- **Checkout gate:** one value, `checkoutLive` in `site/config.js`
  (true since 2026-10-19 per README), gates the Buy surface.
  Payment-Link/product identifiers live in `site/config.js` as
  public configuration; their values are deliberately not
  reproduced in this profile.

## Money surface

This is a live money surface — the MyKey licence checkout:

- **Checkout:** Buy buttons link to Stripe-hosted Payment Link
  pages (company's one Stripe account, 2351485 ALBERTA INC. /
  AIMLDS; Paddle closed 2026-10-14 per README). Stripe redirects
  back to `/buy?checkout=success` (licence) or `/buy?tip=thanks`.
  This site never sees or stores card details (README).
- **Webhook → orders:** `POST /stripe/webhook` (signature-verified,
  see Trust) handles `checkout.session.completed` (Worker L163)
  plus refund/dispute event types, recording orders, refunds and
  disputes in the `MYKEY_ORDERS` KV namespace.
- **Fulfilment:** the desktop repo's issuer polls those orders,
  cross-checks Stripe, mints the MKLIC1 licence key and emails it
  to the buyer; refunds mark the licence for revocation (README
  billing flow steps 1–3).

## How an agent should approach

1. Read `README.md` (checkout state + billing flow are the
   contract), then this profile, then the snapshot; read `site/`
   directly for page content.
2. Keep Download-page versions/SHA-256 in step with the
   `downloads/` artifacts on any release change (README rule).
3. Never move the licence signing key or webhook secrets toward
   this repo; names only in every artifact. Regenerate this
   profile (below) at every material change.

## Regeneration

`docs/codetopo-profile/refresh.sh` (in this pack) re-downloads the repo
at a named ref, re-runs the index, and rewrites `snapshot.json`,
`stats.json` and the header block inputs of this profile. Regenerate at
every release / material change.
