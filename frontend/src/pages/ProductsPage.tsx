import { useQuery } from "@tanstack/react-query";
import { Plus, Search } from "lucide-react";
import { useMemo, useState } from "react";
import { useNavigate } from "react-router";

import { formatCurrency } from "../lib/format";
import { getProducts } from "../services/products";

function ProductsPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");

  const productsQuery = useQuery({
    queryKey: ["products"],
    queryFn: getProducts,
  });

  const filteredProducts = useMemo(() => {
    const products = productsQuery.data ?? [];
    const term = search.trim().toLowerCase();

    if (!term) {
      return products;
    }

    return products.filter(
      (product) =>
        product.name.toLowerCase().includes(term) ||
        product.sku.toLowerCase().includes(term),
    );
  }, [productsQuery.data, search]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">
            Catalogue
          </p>

          <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            Products
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            Manage products, pricing, stock units, and reorder levels.
          </p>
        </div>

        <button
          type="button"
          onClick={() => navigate("/products/new")}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:ring-offset-2"
        >
          <Plus className="h-4 w-4" />
          Add Product
        </button>
      </div>

      <div className="mt-6 rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 p-4">
          <div className="flex max-w-md items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 focus-within:border-slate-400 focus-within:bg-white">
            <Search className="h-4 w-4 shrink-0 text-slate-400" />

            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search products or SKU..."
              aria-label="Search products"
              className="w-full bg-transparent text-sm text-slate-900 outline-none placeholder:text-slate-400"
            />
          </div>
        </div>

        {productsQuery.isLoading && (
          <div className="p-8 text-center">
            <p className="text-sm font-medium text-slate-700">
              Loading products...
            </p>

            <p className="mt-1 text-xs text-slate-500">
              Retrieving your product catalogue.
            </p>
          </div>
        )}

        {productsQuery.isError && (
          <div
            role="alert"
            className="p-8 text-center"
          >
            <p className="text-sm font-semibold text-red-700">
              Unable to load products
            </p>

            <p className="mt-1 text-sm text-slate-500">
              Please try again or check that the BizNuru API is available.
            </p>

            <button
              type="button"
              onClick={() => void productsQuery.refetch()}
              className="mt-4 rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:ring-offset-2"
            >
              Try Again
            </button>
          </div>
        )}

        {!productsQuery.isLoading &&
          !productsQuery.isError &&
          filteredProducts.length === 0 && (
            <div className="p-10 text-center">
              <p className="text-sm font-semibold text-slate-900">
                No products found
              </p>

              <p className="mt-1 text-sm text-slate-500">
                {search
                  ? "Try a different product name or SKU."
                  : "Add your first product to start managing your catalogue."}
              </p>

              {!search && (
                <button
                  type="button"
                  onClick={() => navigate("/products/new")}
                  className="mt-4 inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:ring-offset-2"
                >
                  <Plus className="h-4 w-4" />
                  Add Your First Product
                </button>
              )}
            </div>
          )}

        {!productsQuery.isLoading &&
          !productsQuery.isError &&
          filteredProducts.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[800px]">
                <caption className="sr-only">
                  Product catalogue
                </caption>

                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50/70">
                    <th
                      scope="col"
                      className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500"
                    >
                      Product
                    </th>

                    <th
                      scope="col"
                      className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500"
                    >
                      SKU
                    </th>

                    <th
                      scope="col"
                      className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500"
                    >
                      Unit
                    </th>

                    <th
                      scope="col"
                      className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500"
                    >
                      Cost
                    </th>

                    <th
                      scope="col"
                      className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500"
                    >
                      Selling Price
                    </th>

                    <th
                      scope="col"
                      className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500"
                    >
                      Reorder Level
                    </th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-slate-100">
                  {filteredProducts.map((product) => (
                    <tr
                      key={product.id}
                      className="transition hover:bg-slate-50"
                    >
                      <td className="px-5 py-4">
                        <p className="text-sm font-medium text-slate-900">
                          {product.name}
                        </p>

                        {product.description && (
                          <p className="mt-0.5 max-w-xs truncate text-xs text-slate-500">
                            {product.description}
                          </p>
                        )}
                      </td>

                      <td className="px-5 py-4 text-sm text-slate-600">
                        {product.sku}
                      </td>

                      <td className="px-5 py-4 text-sm text-slate-600">
                        {product.unit}
                      </td>

                      <td className="px-5 py-4 text-right text-sm text-slate-700">
                        {formatCurrency(product.cost_price)}
                      </td>

                      <td className="px-5 py-4 text-right text-sm font-medium text-slate-900">
                        {formatCurrency(product.selling_price)}
                      </td>

                      <td className="px-5 py-4 text-right text-sm text-slate-700">
                        {product.reorder_level}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
      </div>

      {!productsQuery.isLoading &&
        !productsQuery.isError &&
        filteredProducts.length > 0 && (
          <div className="mt-3 flex justify-between px-1 text-xs text-slate-500">
            <span>
              Showing {filteredProducts.length}{" "}
              {filteredProducts.length === 1
                ? "product"
                : "products"}
            </span>

            {search && (
              <span>
                Filtered from {productsQuery.data?.length ?? 0} total
              </span>
            )}
          </div>
        )}
    </div>
  );
}

export default ProductsPage;