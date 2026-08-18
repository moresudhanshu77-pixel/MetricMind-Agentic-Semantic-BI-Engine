import { AskResponse } from "@/types";

export const DEMO_MARGIN_BY_STATUS: AskResponse = {
  question: "What is our total revenue and margin percentage by order status?",
  mode: "simple",
  cube_query: {
    measures: ["fct_orders.total_revenue", "fct_orders.margin_pct"],
    dimensions: ["fct_orders.order_status"],
  },
  data: [
    { "fct_orders.order_status": "delivered", "fct_orders.total_revenue": "131494.56", "fct_orders.margin_pct": "0.83785907" },
    { "fct_orders.order_status": "shipped", "fct_orders.total_revenue": "1317.08", "fct_orders.margin_pct": "0.79084034" },
    { "fct_orders.order_status": "invoiced", "fct_orders.total_revenue": "1069.35", "fct_orders.margin_pct": "0.87636415" },
    { "fct_orders.order_status": "canceled", "fct_orders.total_revenue": "454.89", "fct_orders.margin_pct": "0.82191299" },
  ],
  explanation:
    "Delivered orders generated the most revenue at $131,494.56 with a strong 83.8% margin. Invoiced orders had the highest margin at 87.6%, while shipped orders had the lowest at 79.1%. Overall, the business maintains healthy margins across all order statuses.",
};

export const DEMO_MARGIN_BY_CATEGORY: AskResponse = {
  question: "Why is our margin so low overall?",
  mode: "investigative",
  cube_query: {
    measures: ["fct_orders.total_revenue", "fct_orders.total_estimated_margin", "fct_orders.margin_pct"],
    dimensions: ["fct_orders.order_status"],
  },
  breakdown_query: {
    measures: ["fct_order_items.total_revenue", "fct_order_items.total_margin", "fct_order_items.margin_pct"],
    dimensions: ["fct_order_items.product_category"],
  },
  data: [
    { "fct_orders.order_status": "delivered", "fct_orders.total_revenue": "131494.56", "fct_orders.margin_pct": "0.83785907" },
  ],
  breakdown_data: [
    { "fct_order_items.product_category": "fixed_telephony", "fct_order_items.total_revenue": "7349.99", "fct_order_items.margin_pct": "0.98164487" },
    { "fct_order_items.product_category": "watches_gifts", "fct_order_items.total_revenue": "13965.31", "fct_order_items.margin_pct": "0.92695185" },
    { "fct_order_items.product_category": "sports_leisure", "fct_order_items.total_revenue": "11172.83", "fct_order_items.margin_pct": "0.83764633" },
    { "fct_order_items.product_category": "bed_bath_table", "fct_order_items.total_revenue": "10617.79", "fct_order_items.margin_pct": "0.79467290" },
    { "fct_order_items.product_category": "small_appliances", "fct_order_items.total_revenue": "347.61", "fct_order_items.margin_pct": "0.59201404" },
    { "fct_order_items.product_category": "market_place", "fct_order_items.total_revenue": "39.80", "fct_order_items.margin_pct": "0.29145729" },
  ],
  explanation:
    "The categories with the lowest margins are market_place (29.1%) and small_appliances (59.2%), which are dragging down the overall average. In contrast, fixed_telephony (98.2%) and watches_gifts (92.7%) are the strongest performers. Focusing on pricing or cost structure in the underperforming categories would improve overall margin.",
};