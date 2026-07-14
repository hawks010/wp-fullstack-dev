# WooCommerce development

Treat WooCommerce objects as domain objects. Use `wc_get_order()`, product/order CRUD, data stores, and supported hooks instead of direct post/meta assumptions.

- Declare HPOS compatibility on `before_woocommerce_init` only after the extension avoids incompatible storage access.
- Guard optional classes and functions so the plugin fails gracefully when WooCommerce is inactive.
- Use product/order status transitions deliberately; make callbacks idempotent because webhooks and scheduled actions can retry.
- Do not trigger real payments in routine QA. Prefer test mode, no-charge smoke tests, mocks, or explicit approval for a real charge.
- Escape product-tab and account output. Validate ownership and capabilities for order/customer data.
- For expensive work, use Action Scheduler and preserve observability without logging sensitive payment or customer details.

Test with HPOS enabled and disabled when compatibility is claimed, and cover activation without WooCommerce. See `live-site-safety.md` for production stores.
