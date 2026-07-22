WITH order_items AS (
    SELECT * FROM {{ ref('stg_order_items') }}
),

orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

products AS (
    SELECT * FROM {{ ref('stg_products') }}
),

category AS (
    SELECT * FROM {{ ref('stg_category') }}
)

SELECT
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp,
    p.product_category_name,
    c.product_category_name_english,
    oi.price AS revenue,
    oi.freight_value AS shipping_cost,
    (oi.price - oi.freight_value) AS estimated_margin,
    CASE 
        WHEN oi.price > 0 
        THEN (oi.price - oi.freight_value) / oi.price 
        ELSE NULL 
    END AS margin_pct
FROM order_items oi
LEFT JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN products p ON oi.product_id = p.product_id
LEFT JOIN category c ON p.product_category_name = c.product_category_name