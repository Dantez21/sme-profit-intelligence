export interface ProfitSummary {
  revenue: string;
  cogs: string;
  gross_profit: string;
  gross_margin: string;
}

export interface ProductProfitability {
  product_id: number;
  quantity_sold: string;
  revenue: string;
  cogs: string;
  gross_profit: string;
  gross_margin: string;
}

export interface InventoryProduct {
  product_id: number;
  product_name: string;
  sku: string;
  warehouse_id: number;
  warehouse_name: string;
  current_stock: string;
  reorder_level: string;
  stock_value: string;
  low_stock: boolean;
}

export interface InventoryIntelligence {
  total_stock_value: string;
  low_stock_products: number;
  products: InventoryProduct[];
}

export interface RevenueTrend {
  period: string;
  revenue: string;
  cogs: string;
  gross_profit: string;
}