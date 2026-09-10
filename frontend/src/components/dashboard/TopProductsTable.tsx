import { Trophy } from "lucide-react";

import type { ProductProfitability } from "../../types/intelligence";
import {
  formatCurrency,
  formatPercentage,
  formatQuantity,
} from "../../lib/format";

interface TopProductsTableProps {
  products: ProductProfitability[];
}

function TopProductsTable({
  products,
}: TopProductsTableProps) {
  if (products.length === 0) {
    return (
      <div className="flex min-h-56 items-center justify-center px-6">
        <div className="text-center">
          <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-slate-100">
            <Trophy className="h-5 w-5 text-slate-400" />
          </div>

          <p className="mt-3 text-sm font-semibold text-slate-900">
            No product performance data
          </p>

          <p className="mt-1 text-sm text-slate-500">
            Product performance will appear once submitted sales are recorded.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[720px]">
        <thead>
          <tr className="border-b border-slate-200 bg-slate-50/70">
            <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Product
            </th>

            <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
              Units Sold
            </th>

            <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
              Revenue
            </th>

            <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
              Gross Profit
            </th>

            <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
              Margin
            </th>
          </tr>
        </thead>

        <tbody className="divide-y divide-slate-100">
          {products.slice(0, 5).map((product, index) => (
            <tr key={product.product_id} className="hover:bg-slate-50">
              <td className="px-5 py-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-bold text-slate-600">
                    {index + 1}
                  </div>

                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-slate-900">
                      {product.product_name}
                    </p>

                    <p className="mt-0.5 text-xs text-slate-500">
                      {product.sku}
                    </p>
                  </div>
                </div>
              </td>

              <td className="px-5 py-4 text-right text-sm text-slate-700">
                {formatQuantity(product.quantity_sold)}
              </td>

              <td className="px-5 py-4 text-right text-sm font-medium text-slate-900">
                {formatCurrency(product.revenue)}
              </td>

              <td className="px-5 py-4 text-right text-sm font-medium text-slate-900">
                {formatCurrency(product.gross_profit)}
              </td>

              <td className="px-5 py-4 text-right text-sm font-semibold text-slate-700">
                {formatPercentage(product.gross_margin)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TopProductsTable;
