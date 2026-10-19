/* Stripe checkout — active ONLY when config.checkoutLive is true.
 * The Buy buttons are plain links to Stripe-hosted Payment Link
 * pages (see config.js). No payment code runs on this site and no
 * card detail ever touches it. While checkoutLive is false, the
 * Buy page keeps its honest fallback card and no purchase control
 * is shown. */
(function () {
  var cfg = window.MYKEY_CONFIG || {};
  if (!cfg.checkoutLive || !cfg.stripe || !cfg.stripe.links) return;
  var off = document.getElementById("checkout-off");
  var on = document.getElementById("checkout-on");
  if (!on) return;
  if (off) off.style.display = "none";
  on.style.display = "block";

  var links = {
    "buy-licence-suggested": cfg.stripe.links.licenceSuggested,
    "buy-licence-floor": cfg.stripe.links.licenceFloor,
    "buy-tip-5": cfg.stripe.links.tip5,
    "buy-tip-3": cfg.stripe.links.tip3
  };
  Object.keys(links).forEach(function (id) {
    var el = document.getElementById(id);
    if (el) {
      el.addEventListener("click", function () {
        window.location.href = links[id];
      });
    }
  });

  /* Stripe sends buyers back to /buy?checkout=success (licence)
   * or /buy?tip=thanks (patron tip) after payment. */
  var q = new URLSearchParams(window.location.search);
  if (q.get("checkout") === "success") {
    var paid = document.getElementById("paid-note");
    if (paid) paid.style.display = "block";
  }
  if (q.get("tip") === "thanks") {
    var tip = document.getElementById("tip-note");
    if (tip) tip.style.display = "block";
  }
})();
