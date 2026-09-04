# Training-only EDA findings

- Structure: 67,533 training rows, 34 source columns, 58.58 MB; late rate 7.83%.
- Time: 2016-09-15 12:16:38 through 2018-04-15 20:07:56; month, weekday, hour, and Brazilian national purchase-holiday effects were measured.
- Missingness was quantified and compared with target rates for product and geography candidates; preprocessing will use train-fitted median/mode imputation.
- Numerical distributions are right-skewed and contain IQR outliers, so scaling is appropriate; valid large purchases are not deleted.
- Negative monetary values found: False (affected rows: 0).
- Raw customer coordinate ranges are latitude [-33.690971840060584, 41.14620290949943] and longitude [-72.67098698091266, -8.57785501800488]; 3 training rows lie outside explicit Brazil bounds and are not used for distance.
- Validated Haversine mean/max distance is available; late-rate spread across distance quintiles is 7.25%. Same-state-group spread is 8.97%.
- Customer-state late rates range from 3.78% to 24.83% for states with at least 100 orders; seller-state and customer/seller same-state relationships were also inspected.
- Customer ZIP prefix has 13,748 training categories and dominant seller ZIP prefix has 1,679 and is excluded to avoid high-cardinality memorization.
- `promised_window_days` and `freight_price_ratio` were summarized and correlated with `late` before retention. Purchase-holiday late-rate difference is 2.55% and is retained as a low-complexity reproducible calendar flag.
- Outcome-only actual delivery days and delay days were analyzed descriptively but are forbidden model inputs.
- Retained feature groups: order/item/payment/product aggregates, customer_state, dominant_seller_state, dominant_product_category, dominant_payment_type, purchase calendar, promised_window_days, freight_price_ratio, purchase_is_holiday, mean/max customer_seller_distance_km, same_state_share.
- Excluded groups: raw latitude/longitude (quality risk and less interpretable than validated distance), ZIP prefix (high cardinality), identifiers, future/outcome fields, reviews.
- Explicit future/outcome-only columns: order_status, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, delivery_delta_hours. Explicit identifiers: order_id, customer_id, customer_unique_id.
