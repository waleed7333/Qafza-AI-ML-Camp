CREATE SCHEMA IF NOT EXISTS raw;

DROP TABLE IF EXISTS
    raw.order_reviews,
    raw.order_payments,
    raw.order_items,
    raw.orders,
    raw.products,
    raw.sellers,
    raw.customers,
    raw.category_translation,
    raw.geolocation
CASCADE;

CREATE TABLE raw.customers (
    customer_id char(32) PRIMARY KEY,
    customer_unique_id char(32) NOT NULL,
    customer_zip_code_prefix char(5) NOT NULL,
    customer_city text NOT NULL,
    customer_state char(2) NOT NULL
);

CREATE TABLE raw.geolocation (
    geolocation_zip_code_prefix char(5) NOT NULL,
    geolocation_lat double precision NOT NULL,
    geolocation_lng double precision NOT NULL,
    geolocation_city text NOT NULL,
    geolocation_state char(2) NOT NULL
);

CREATE TABLE raw.products (
    product_id char(32) PRIMARY KEY,
    product_category_name text,
    product_name_lenght integer,
    product_description_lenght integer,
    product_photos_qty integer,
    product_weight_g integer,
    product_length_cm integer,
    product_height_cm integer,
    product_width_cm integer
);

CREATE TABLE raw.sellers (
    seller_id char(32) PRIMARY KEY,
    seller_zip_code_prefix char(5) NOT NULL,
    seller_city text NOT NULL,
    seller_state char(2) NOT NULL
);

CREATE TABLE raw.category_translation (
    product_category_name text PRIMARY KEY,
    product_category_name_english text NOT NULL
);

CREATE TABLE raw.orders (
    order_id char(32) PRIMARY KEY,
    customer_id char(32) NOT NULL REFERENCES raw.customers (customer_id),
    order_status text NOT NULL,
    order_purchase_timestamp timestamp without time zone NOT NULL,
    order_approved_at timestamp without time zone,
    order_delivered_carrier_date timestamp without time zone,
    order_delivered_customer_date timestamp without time zone,
    order_estimated_delivery_date timestamp without time zone NOT NULL
);

CREATE TABLE raw.order_items (
    order_id char(32) NOT NULL REFERENCES raw.orders (order_id),
    order_item_id integer NOT NULL,
    product_id char(32) NOT NULL REFERENCES raw.products (product_id),
    seller_id char(32) NOT NULL REFERENCES raw.sellers (seller_id),
    shipping_limit_date timestamp without time zone NOT NULL,
    price numeric(12, 2) NOT NULL,
    freight_value numeric(12, 2) NOT NULL,
    PRIMARY KEY (order_id, order_item_id)
);

CREATE TABLE raw.order_payments (
    order_id char(32) NOT NULL REFERENCES raw.orders (order_id),
    payment_sequential integer NOT NULL,
    payment_type text NOT NULL,
    payment_installments integer NOT NULL,
    payment_value numeric(12, 2) NOT NULL,
    PRIMARY KEY (order_id, payment_sequential)
);

CREATE TABLE raw.order_reviews (
    review_id char(32) NOT NULL,
    order_id char(32) NOT NULL REFERENCES raw.orders (order_id),
    review_score integer NOT NULL,
    review_comment_title text,
    review_comment_message text,
    review_creation_date timestamp without time zone NOT NULL,
    review_answer_timestamp timestamp without time zone NOT NULL
);

CREATE INDEX geolocation_zip_idx ON raw.geolocation (geolocation_zip_code_prefix);
CREATE INDEX orders_customer_idx ON raw.orders (customer_id);
CREATE INDEX order_items_product_idx ON raw.order_items (product_id);
CREATE INDEX order_items_seller_idx ON raw.order_items (seller_id);
CREATE INDEX order_payments_order_idx ON raw.order_payments (order_id);
CREATE INDEX order_reviews_order_idx ON raw.order_reviews (order_id);
CREATE INDEX order_reviews_review_idx ON raw.order_reviews (review_id);
