/* Paddle checkout — active ONLY when config.checkoutLive is true.
 * While it is false, the Buy page keeps its honest "checkout opens
 * at launch" note and no purchase control is shown. */
(function () {
  var cfg = window.MYKEY_CONFIG || {};
  if (!cfg.checkoutLive || !cfg.paddle) return;
  var off = document.getElementById("checkout-off");
  var on = document.getElementById("checkout-on");
  if (!on) return;
  if (off) off.style.display = "none";
  on.style.display = "block";

  var script = document.createElement("script");
  script.src = "https://cdn.paddle.com/paddle/paddle.js";
  script.onload = function () {
    if (cfg.paddle.environment === "sandbox" && window.Paddle.Environment) {
      window.Paddle.Environment.set("sandbox");
    }
    window.Paddle.Initialize({ token: cfg.paddle.clientToken });
    on.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-price-id]");
      if (!btn) return;
      window.Paddle.Checkout.open({ items: [{ priceId: btn.getAttribute("data-price-id"), quantity: 1 }] });
    });
  };
  document.head.appendChild(script);

  var map = {
    "buy-licence-suggested": cfg.paddle.prices.licenceSuggested,
    "buy-licence-floor": cfg.paddle.prices.licenceFloor,
    "buy-tip-5": cfg.paddle.prices.tip5,
    "buy-tip-3": cfg.paddle.prices.tip3
  };
  Object.keys(map).forEach(function (id) {
    var el = document.getElementById(id);
    if (el) el.setAttribute("data-price-id", map[id]);
  });
})();
