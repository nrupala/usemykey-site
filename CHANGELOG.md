# Changelog

## 2026-10-14 — The vault's home (Android) + APK refresh

- Android APK refreshed to client 1.4.0 (SHA-256 13ec2578…): the
  vault can now live outside the app. Give it a home folder once
  and MyKey keeps the encrypted vault file there, updated on every
  save — uninstalling the app no longer takes your vault with it,
  and a reinstall finds the vault in its folder. Signed with the
  same permanent MyKey release key as the previous build, so this
  update installs in place.

## 2026-10-14 — Permanently signed Android build + APK refresh

- Android APK refreshed (SHA-256 a7bd97f8…): the app is now built
  as a release build and signed with the permanent MyKey release
  key, so updates install in place from this build onward. Earlier
  test builds were debug-signed with throwaway keys and could not
  be updated over — the download page now says so plainly, with
  the export-first step for anyone coming from a test build.

## 2026-10-14 — New logo + APK refresh

- Favicon is now the product mark: the refined-key logo (two-tone
  gold key, double-ring bow, deep navy #111D54), replacing the
  green/white placeholder.
- Android APK refreshed (SHA-256 63f64709…): the same client with
  the new logo in every launcher icon (adaptive + legacy mipmaps).

## 2026-10-14 — APK refresh: Help visible on the locked screen

- Android APK refreshed (SHA-256 470c13fe…). The client fix moves
  the "Help and questions" button on the locked screen to directly
  under the unlock controls, before the secondary actions — on a
  phone it previously fell below the fold.

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
