export interface Product {
  id: number;
  name: string;
  sku: string;
  description: string | null;
  category_id: number;
  unit: string;
  cost_price: string;
  selling_price: string;
  reorder_level: string;
  created_at: string;
  updated_at: string;
}
