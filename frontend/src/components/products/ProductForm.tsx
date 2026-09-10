import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { getCategories } from "../../services/categories";
import type { ProductCreate } from "../../services/products";

interface ProductFormProps {
  onSubmit: (data: ProductCreate) => void;
  isSubmitting?: boolean;
  error?: string;
}

function ProductForm({
  onSubmit,
  isSubmitting = false,
  error,
}: ProductFormProps) {
  const categoriesQuery = useQuery({
    queryKey: ["categories"],
    queryFn: getCategories,
  });

  const [form, setForm] = useState<ProductCreate>({
    name: "",
    sku: "",
    description: "",
    category_id: 0,
    unit: "pcs",
    cost_price: "",
    selling_price: "",
    reorder_level: "0",
  });

  const updateField = (
    field: keyof ProductCreate,
    value: string | number,
  ) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    onSubmit({
      ...form,
      name: form.name.trim(),
      sku: form.sku.trim(),
      description: form.description?.trim() || undefined,
    });
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-xl border border-slate-200 bg-white shadow-sm"
    >
      <div className="border-b border-slate-200 px-5 py-4">
        <h2 className="font-semibold text-slate-900">
          Product Information
        </h2>
        <p className="mt-1 text-xs text-slate-500">
          Add the product details used for sales, inventory, and profitability.
        </p>
      </div>

      <div className="grid gap-5 p-5 sm:grid-cols-2">
        <div className="sm:col-span-2">
          <label className="block text-sm font-medium text-slate-700">
            Product Name
          </label>
          <input
            required
            value={form.name}
            onChange={(event) =>
              updateField("name", event.target.value)
            }
            placeholder="e.g. Ribeye Steak"
            className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:ring-1 focus:ring-slate-900"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700">
            SKU
          </label>
          <input
            required
            value={form.sku}
            onChange={(event) =>
              updateField("sku", event.target.value)
            }
            placeholder="e.g. BEEF-001"
            className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:ring-1 focus:ring-slate-900"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700">
            Category
          </label>
          <select
            required
            value={form.category_id}
            onChange={(event) =>
              updateField(
                "category_id",
                Number(event.target.value),
              )
            }
            disabled={categoriesQuery.isLoading}
            className="mt-1.5 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:ring-1 focus:ring-slate-900"
          >
            <option value={0}>Select category</option>
            {categoriesQuery.data?.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700">
            Unit
          </label>
          <input
            required
            value={form.unit}
            onChange={(event) =>
              updateField("unit", event.target.value)
            }
            placeholder="pcs, kg, litre..."
            className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:ring-1 focus:ring-slate-900"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700">
            Reorder Level
          </label>
          <input
            required
            min="0"
            step="0.001"
            type="number"
            value={form.reorder_level}
            onChange={(event) =>
              updateField(
                "reorder_level",
                event.target.value,
              )
            }
            className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:ring-1 focus:ring-slate-900"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700">
            Cost Price
          </label>
          <input
            required
            min="0"
            step="0.01"
            type="number"
            value={form.cost_price}
            onChange={(event) =>
              updateField(
                "cost_price",
                event.target.value,
              )
            }
            placeholder="0.00"
            className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:ring-1 focus:ring-slate-900"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700">
            Selling Price
          </label>
          <input
            required
            min="0"
            step="0.01"
            type="number"
            value={form.selling_price}
            onChange={(event) =>
              updateField(
                "selling_price",
                event.target.value,
              )
            }
            placeholder="0.00"
            className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:ring-1 focus:ring-slate-900"
          />
        </div>

        <div className="sm:col-span-2">
          <label className="block text-sm font-medium text-slate-700">
            Description
          </label>
          <textarea
            rows={4}
            value={form.description}
            onChange={(event) =>
              updateField(
                "description",
                event.target.value,
              )
            }
            placeholder="Optional product description..."
            className="mt-1.5 w-full resize-none rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:ring-1 focus:ring-slate-900"
          />
        </div>
      </div>

      {error && (
        <div className="mx-5 mb-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="flex justify-end border-t border-slate-200 px-5 py-4">
        <button
          type="submit"
          disabled={isSubmitting || categoriesQuery.isLoading}
          className="rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSubmitting ? "Creating..." : "Create Product"}
        </button>
      </div>
    </form>
  );
}

export default ProductForm;
