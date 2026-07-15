# WooCommerce development

Treat WooCommerce objects as domain objects. Use `wc_get_order()`, product/order CRUD, data stores, and supported hooks instead of direct post/meta assumptions.

- Declare HPOS compatibility on `before_woocommerce_init` only after the extension avoids incompatible storage access.
- Guard optional classes and functions so the plugin fails gracefully when WooCommerce is inactive.
- Use product/order status transitions deliberately; make callbacks idempotent because webhooks and scheduled actions can retry.
- Do not trigger real payments in routine QA. Prefer test mode, no-charge smoke tests, mocks, or explicit approval for a real charge.
- Escape product-tab and account output. Validate ownership and capabilities for order/customer data.
- For expensive work, use Action Scheduler and preserve observability without logging sensitive payment or customer details.

Test with HPOS enabled and disabled when compatibility is claimed, and cover activation without WooCommerce. See `live-site-safety.md` for production stores.

## Cart and Checkout blocks

WooCommerce's block-based Cart and Checkout (the `woocommerce/cart` and `woocommerce/checkout` blocks, default since WC 8.3) use a different extension surface than the legacy shortcode checkout. Hooks like `woocommerce_before_checkout_form`, `woocommerce_checkout_update_order_meta`, and `woocommerce_review_order_before_payment` do not fire on block checkout — code relying only on those hooks silently does nothing for merchants using blocks.

- Detect which checkout is active before assuming hook-based extension points will fire: check whether the Checkout page content contains the `woocommerce/checkout` block, or use `Automattic\WooCommerce\Blocks\Package::container()` availability as a proxy for block support.
- Extend cart/checkout data with the Store API `ExtendSchema` mechanism (`woocommerce_store_api_register_endpoint_data`), not post meta writes assumed from legacy hooks.
- Register block-based payment methods via `Automattic\WooCommerce\Blocks\Payments\Integrations\AbstractPaymentMethodType` and `IntegrationRegistry`, in addition to the legacy `WC_Payment_Gateway` class if the extension must support both checkouts.
- Client-side additions (fields, slots) use `@woocommerce/blocks-checkout` filter registries (`ExperimentalOrderMeta`, `checkoutBlocksFilterRegistry`), not admin-side PHP templating.
- If an extension must support both the legacy shortcode and block checkout, implement both extension paths explicitly and note in code comments which is which — do not assume one implies the other.
