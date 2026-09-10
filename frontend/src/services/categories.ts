import { apiFetch } from "../lib/api";
import type { Category } from "../types/category";

export interface CategoryCreate {
  name: string;
  description?: string;
}

export interface CategoryUpdate {
  name?: string;
  description?: string;
}

export function getCategories() {
  return apiFetch<Category[]>("/api/v1/categories");
}

export function createCategory(data: CategoryCreate) {
  return apiFetch<Category>("/api/v1/categories", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateCategory(
  categoryId: number,
  data: CategoryUpdate,
) {
  return apiFetch<Category>(
    `/api/v1/categories/${categoryId}`,
    {
      method: "PUT",
      body: JSON.stringify(data),
    },
  );
}

export async function deleteCategory(
  categoryId: number,
): Promise<void> {
  await apiFetch<void>(
    `/api/v1/categories/${categoryId}`,
    {
      method: "DELETE",
    },
  );
}
