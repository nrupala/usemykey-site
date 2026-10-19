/* MyKey site configuration — the ONE place checkout state lives.
 *
 * checkoutLive is TRUE: payments run on the company's one Stripe
 * account (2351485 ALBERTA INC., public name AIMLDS) — payments
 * were consolidated on Stripe on 2026-10-14 and Paddle is closed.
 * The Buy page links out to Stripe-hosted Payment Link pages;
 * this site never sees or stores card details.
 *
 * How a licence reaches the buyer: after payment, Stripe calls
 * this site's webhook (POST /stripe/webhook on the Worker). The
 * Worker verifies Stripe's signature and records the order; an
 * issuer step under the company's licence authority then mints
 * the buyer's MKLIC1 licence key and emails it to the address
 * used at checkout. The patron tip prices are plain
 * subscriptions — they unlock nothing.
 *
 * Prices: the licence is pay-what-you-want — the suggested price
 * is a customer-set amount (preset US$49, minimum US$29, maximum
 * US$999); the floor price is a fixed US$29. Both mint the same
 * licence.
 */
window.MYKEY_CONFIG = {
  checkoutLive: true,
  stripe: {
    account: "acct_1UQdZREAiA4GKFhA",
    products: {
      licence: "prod_VTDWA8emf39Stw",
      tip: "prod_VTDWn8YgvaizwU"
    },
    prices: {
      licenceSuggested: "price_1USH6BEAiA4GKFhA9scCt7HO",
      licenceFloor: "price_1USH5NEAiA4GKFhAltrszAVT",
      tip5: "price_1USH5OEAiA4GKFhAQ6LQbXau",
      tip3: "price_1USH5QEAiA4GKFhAZXKJlTAh"
    },
    links: {
      licenceSuggested: "https://buy.stripe.com/3cIfZh1m2bEI3mD32C9Zm06",
      licenceFloor: "https://buy.stripe.com/dRm7sL7KqbEIe1heLk9Zm07",
      tip5: "https://buy.stripe.com/8x28wPd4KgZ2e1hfPo9Zm08",
      tip3: "https://buy.stripe.com/cNi5kDd4K6ko8GX1Yy9Zm09"
    }
  },
  apk: {
    version: "1.4.0",
    sizeBytes: 6128415,
    sha256: "13ec25788fa02aa57b059f992b0414c32a0bdeb95d81e8d569c6d2496aa22e55",
    file: "MyKey.apk"
  }
};
