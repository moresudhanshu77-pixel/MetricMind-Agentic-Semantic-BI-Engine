WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

order_items AS (
    SELECT * FROM {{ ref('stg_order_items') }}
),

order_item_agg AS (
    SELECT
        order_id,
        SUM(price) AS total_price,
        SUM(freight_value) AS total_freight,
        COUNT(order_item_id) AS num_items
    FROM order_items
    GROUP BY order_id
)

SELECT
    o.order_id,
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    oi.total_price AS revenue,
    oi.total_freight AS shipping_cost,
    oi.num_items,
    (oi.total_price - oi.total_freight) AS estimated_margin,
    CASE 
        WHEN oi.total_price > 0 
        THEN (oi.total_price - oi.total_freight) / oi.total_price 
        ELSE NULL 
    END AS margin_pct
FROM orders o
LEFT JOIN order_item_agg oi ON o.order_id = oi.order_id