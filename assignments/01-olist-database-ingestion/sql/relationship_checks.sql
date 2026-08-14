-- Each query must return zero. They deliberately avoid joining multiple
-- one-to-many relations, which could multiply rows and monetary values.
SELECT count(*) AS orphan_orders FROM raw.orders o
LEFT JOIN raw.customers c ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL;

SELECT count(*) AS orphan_items_orders FROM raw.order_items i
LEFT JOIN raw.orders o ON o.order_id = i.order_id
WHERE o.order_id IS NULL;

SELECT count(*) AS orphan_items_products FROM raw.order_items i
LEFT JOIN raw.products p ON p.product_id = i.product_id
WHERE p.product_id IS NULL;

SELECT count(*) AS orphan_items_sellers FROM raw.order_items i
LEFT JOIN raw.sellers s ON s.seller_id = i.seller_id
WHERE s.seller_id IS NULL;

SELECT count(*) AS orphan_payments FROM raw.order_payments p
LEFT JOIN raw.orders o ON o.order_id = p.order_id
WHERE o.order_id IS NULL;

SELECT count(*) AS orphan_reviews FROM raw.order_reviews r
LEFT JOIN raw.orders o ON o.order_id = r.order_id
WHERE o.order_id IS NULL;

-- Informational: this is nonzero in the source, so no category FK is imposed.
SELECT count(*) AS products_with_untranslated_category
FROM raw.products p
LEFT JOIN raw.category_translation t
  ON t.product_category_name = p.product_category_name
WHERE p.product_category_name IS NOT NULL
  AND t.product_category_name IS NULL;
