SELECT
    p.product_id,
    p.product_category_name,
    c.product_category_name_english,
    p.product_weight_g
FROM {{ ref('stg_products') }} p
LEFT JOIN {{ ref('stg_category') }} c 
    ON p.product_category_name = c.product_category_name