# Changelog

## 2026-10-13 — All feature waves merged; downloads completed

- Home now describes what shipped with the feature waves: passkeys,
  the browser extension, Android autofill, built-in help, and the
  adjustable 1–5 minute clipboard clear.
- Download page: Android APK refreshed to client 1.3.0 (SHA-256
  5459c299…); desktop downloads are real files now — MyKey 2.2.0
  Windows app + CLI and the Linux bundle, hosted in `downloads/`
  alongside the APK and served by the same Worker redirects, with
  the SHA-256 checksums file beside them. Builds are unsigned; the
  page says so with the SmartScreen steps. macOS still has no
  prebuilt download (build script only).
- New Browser extension section: store listings pending, install
  package + instructions on the project page.
- `tools/build_deploy.py` verify markers updated to the new copy
  and checksums.
- Checkout unchanged: still behind `checkoutLive: false` until the
  owner's Paddle live seller verification is complete.

## 2026-10-13 — Site launch

- First public version of usemykey.com: Home, Download, Buy, Recover,
  Support & FAQ, Privacy, Terms, plus llms.txt / robots / sitemap /
  security.txt.
- Android APK 1.2.0 (SHA-256 d9f4750c…) served from `downloads/`.
- Checkout wired to Paddle Sandbox behind the single `checkoutLive`
  flag in `site/config.js` (off — no live Paddle account yet, so the
  Buy page shows "Checkout opens at launch").
