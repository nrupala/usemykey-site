/* MyKey site configuration — the ONE place checkout state lives.
 *
 * checkoutLive is false: there is no live Paddle account for
 * 2351485 ALBERTA INC. yet (the seller verification step is the
 * owner's). The Buy page therefore shows "checkout opens at launch"
 * and never presents the sandbox checkout as a real purchase.
 *
 * To open checkout at launch:
 *   1. Complete Paddle live seller verification for the Inc.
 *   2. Create the live products/prices + a live client token.
 *   3. Set environment to "production", fill in the live token and
 *      price IDs below, and set checkoutLive to true.
 * The sandbox values below are real Paddle Sandbox objects, created
 * 2026-10-13, so the full checkout can be exercised in test mode.
 */
window.MYKEY_CONFIG = {
  checkoutLive: false,
  paddle: {
    environment: "sandbox",
    clientToken: "test_ecb0286d3fbd0d3c67d4e48c8f2",
    prices: {
      licenceSuggested: "pri_01m4v87pjaxkatmemrgzc8swvm",
      licenceFloor: "pri_01m4v87rhp7jsbqpc3exd58vcm",
      tip5: "pri_01m4v87t8aanw1msw48y6vqccp",
      tip3: "pri_01m4v87w2px09jp2gj5m65jcxa"
    }
  },
  apk: {
    version: "1.2.0",
    sizeBytes: 7322173,
    sha256: "d9f4750c149680e774bd13b4ffd255bfd0b4771d000765cb08523d5ac921f968",
    file: "MyKey.apk"
  }
};
