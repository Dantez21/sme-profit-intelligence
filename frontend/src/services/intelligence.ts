import { apiFetch } from "../lib/api";
import type {
  InventoryIntelligence,
  ProductProfitability,
  ProfitSummary,
  RevenueTrend,
} from "../types/intelligence";

export function getProfitSummary() {
  return apiFetch<ProfitSummary>(
    "/api/v1/intelligence/profit-summary",
  );
}

export function getProductProfitability() {
  return apiFetch<ProductProfitability[]>(
    "/api/v1/intelligence/product-profitability",
  );
}

export function getInventoryIntelligence() {
  return apiFetch<InventoryIntelligence>(
    "/api/v1/intelligence/inventory",
  );
}

export function getRevenueTrend() {
  return apiFetch<RevenueTrend[]>(
    "/api/v1/intelligence/revenue-trend",
  );
}