import { apiFetch } from "../lib/api";
import type { Product } from "../types/product";

export interface ProductCreate {
  name: string;
  sku: string;
  description?: string;
  category_id: number;
  unit: string;
  cost_price: string;
  selling_price: string;
  reorder_level: string;
}

export function getProducts() {
  return apiFetch<Product[]>("/api/v1/products");
}

export function getProduct(productId: number) {
  return apiFetch<Product>(`/api/v1/products/${productId}`);
}

export function createProduct(data: ProductCreate) {
  return apiFetch<Product>("/api/v1/products", {
    method: "POST",
    body: JSON.stringify(data),
  });
}