-- Connection and inventory smoke test.
SELECT current_database() AS database_name, current_user AS database_user;

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'raw'
ORDER BY table_name;

-- Required real relationship JOIN: one order maps to one customer row.
SELECT
    o.order_id,
    o.order_status,
    o.order_purchase_timestamp,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state
FROM raw.orders AS o
JOIN raw.customers AS c ON c.customer_id = o.customer_id
ORDER BY o.order_id
LIMIT 10;

-- A second safe JOIN at the item grain (no aggregation of amounts).
SELECT
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    oi.price,
    oi.freight_value
FROM raw.order_items AS oi
JOIN raw.orders AS o ON o.order_id = oi.order_id
ORDER BY oi.order_id, oi.order_item_id
LIMIT 10;
