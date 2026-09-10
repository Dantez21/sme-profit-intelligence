import {
  BarChart3,
  Boxes,
  CircleDollarSign,
  TrendingUp,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";

import DashboardError from "../components/dashboard/DashboardError";
import DashboardLoading from "../components/dashboard/DashboardLoading";
import RevenueProfitChart from "../components/dashboard/RevenueProfitChart";
import StatCard from "../components/dashboard/StatCard";
import TopProductsTable from "../components/dashboard/TopProductsTable";

import {
  getInventoryIntelligence,
  getProductProfitability,
  getProfitSummary,
  getRevenueTrend,
} from "../services/intelligence";

import {
  formatCurrency,
  formatPercentage,
} from "../lib/format";


function DashboardPage() {
  const profitQuery = useQuery({
    queryKey: [
      "intelligence",
      "profit-summary",
    ],
    queryFn: getProfitSummary,
  });

  const inventoryQuery = useQuery({
    queryKey: [
      "intelligence",
      "inventory",
    ],
    queryFn: getInventoryIntelligence,
  });

  const trendQuery = useQuery({
    queryKey: [
      "intelligence",
      "revenue-trend",
    ],
    queryFn: getRevenueTrend,
  });

  const productProfitabilityQuery = useQuery({
    queryKey: ["intelligence", "product-profitability"],
    queryFn: getProductProfitability,
  });

  const isLoading =
    profitQuery.isLoading ||
    inventoryQuery.isLoading ||
    trendQuery.isLoading ||
    productProfitabilityQuery.isLoading;

  const hasError =
    profitQuery.isError ||
    inventoryQuery.isError ||
    trendQuery.isError ||
    productProfitabilityQuery.isError;

  const retry = () => {
    void profitQuery.refetch();
    void inventoryQuery.refetch();
    void trendQuery.refetch();
    void productProfitabilityQuery.refetch();
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">

      {/* Page Header */}
      <div>
        <p className="text-sm font-medium text-slate-500">
          Overview
        </p>

        <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          Business Dashboard
        </h1>

        <p className="mt-2 max-w-2xl text-sm text-slate-500">
          Your business. Your numbers. Your intelligence.
        </p>
      </div>


      {/* Dashboard Content */}
      <div className="mt-8">

        {/* Loading State */}
        {isLoading && (
          <DashboardLoading />
        )}


        {/* Error State */}
        {hasError && !isLoading && (
          <DashboardError
            message="We couldn't retrieve the latest business intelligence."
            onRetry={retry}
          />
        )}


        {/* Successful Dashboard */}
        {!isLoading && !hasError && (
          <>
            {/* KPI Cards */}
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

              <StatCard
                label="Revenue"
                value={formatCurrency(
                  profitQuery.data?.revenue ?? "0",
                )}
                icon={CircleDollarSign}
                description="Submitted sales"
              />


              <StatCard
                label="Gross Profit"
                value={formatCurrency(
                  profitQuery.data?.gross_profit ?? "0",
                )}
                icon={TrendingUp}
                description="Revenue less COGS"
              />


              <StatCard
                label="Gross Margin"
                value={formatPercentage(
                  profitQuery.data?.gross_margin ?? "0",
                )}
                // value={`${Number(
                //   profitQuery.data?.gross_margin ?? "0",
                // ).toFixed(2)}%`}
                icon={BarChart3}
                description="Gross profit percentage"
              />

              <StatCard
                label="Stock Value"
                value={formatCurrency(
                  inventoryQuery.data?.total_stock_value ?? "0",
                )}
                icon={Boxes}
                description={`${inventoryQuery.data?.low_stock_products ?? 0} low-stock products`}
              />

            </div>


            {/* Revenue & Profit Trend */}
            <section className="mt-6 rounded-xl border border-slate-200 bg-white shadow-sm">

              <div className="border-b border-slate-200 px-5 py-4">

                <h2 className="font-semibold text-slate-900">
                  Revenue & Gross Profit
                </h2>

                <p className="mt-1 text-xs text-slate-500">
                  Monthly performance based on submitted sales.
                </p>

              </div>

              <div className="p-5">
                <RevenueProfitChart
                  data={trendQuery.data ?? []}
                />
              </div>

            </section>


            {/* Lower Dashboard Panels */}
            <div className="mt-6 grid gap-6 lg:grid-cols-2">

              {/* Low Stock */}
              <section className="rounded-xl border border-slate-200 bg-white shadow-sm">

                <div className="border-b border-slate-200 px-5 py-4">

                  <h2 className="font-semibold text-slate-900">
                    Low Stock
                  </h2>

                  <p className="mt-1 text-xs text-slate-500">
                    Products at or below their reorder level.
                  </p>

                </div>


                <div className="divide-y divide-slate-100">

                  {(
                    inventoryQuery.data?.products ?? []
                  )
                    .filter(
                      (product) =>
                        product.low_stock,
                    )
                    .slice(0, 5)
                    .map((product) => (

                      <div
                        key={`${product.product_id}-${product.warehouse_id}`}
                        className="flex items-center justify-between gap-4 px-5 py-4"
                      >

                        <div className="min-w-0">

                          <p className="truncate text-sm font-medium text-slate-900">
                            {product.product_name}
                          </p>

                          <p className="mt-0.5 text-xs text-slate-500">
                            {product.warehouse_name}
                          </p>

                        </div>


                        <div className="shrink-0 text-right">

                          <p className="text-sm font-semibold text-red-600">
                            {product.current_stock}
                          </p>

                          <p className="text-xs text-slate-500">
                            Reorder: {product.reorder_level}
                          </p>

                        </div>

                      </div>

                    ))}


                  {(
                    inventoryQuery.data?.products ?? []
                  ).filter(
                    (product) =>
                      product.low_stock,
                  ).length === 0 && (

                    <div className="px-5 py-8 text-center">

                      <p className="text-sm font-medium text-slate-900">
                        Inventory looks healthy
                      </p>

                      <p className="mt-1 text-xs text-slate-500">
                        No products are currently below their reorder level.
                      </p>

                    </div>

                  )}

                </div>

              </section>

              <section className="mt-6 rounded-xl border border-slate-200 bg-white shadow-sm">
                <div className="border-b border-slate-200 px-5 py-4">
                  <h2 className="font-semibold text-slate-900">
                    Top Performing Products
                  </h2>

                  <p className="mt-1 text-xs text-slate-500">
                    Products ranked by revenue from submitted sales.
                  </p>
                </div>

                <TopProductsTable
                  products={productProfitabilityQuery.data ?? []}
                />
              </section>


              {/* Inventory Overview */}
              <section className="rounded-xl border border-slate-200 bg-white shadow-sm">

                <div className="border-b border-slate-200 px-5 py-4">

                  <h2 className="font-semibold text-slate-900">
                    Inventory Overview
                  </h2>

                  <p className="mt-1 text-xs text-slate-500">
                    Current stock position across active warehouses.
                  </p>

                </div>


                <div className="divide-y divide-slate-100">

                  {(
                    inventoryQuery.data?.products ?? []
                  )
                    .slice(0, 5)
                    .map((product) => (

                      <div
                        key={`${product.product_id}-${product.warehouse_id}`}
                        className="flex items-center justify-between gap-4 px-5 py-4"
                      >

                        <div className="min-w-0">

                          <p className="truncate text-sm font-medium text-slate-900">
                            {product.product_name}
                          </p>

                          <p className="mt-0.5 text-xs text-slate-500">
                            {product.sku} ·{" "}
                            {product.warehouse_name}
                          </p>

                        </div>


                        <div className="shrink-0 text-right">

                          <p className="text-sm font-semibold text-slate-900">
                            {formatCurrency(
                              product.stock_value,
                            )}
                          </p>

                          <p className="text-xs text-slate-500">
                            {product.current_stock} units
                          </p>

                        </div>

                      </div>

                    ))}


                  {(
                    inventoryQuery.data?.products ?? []
                  ).length === 0 && (

                    <div className="px-5 py-8 text-center">

                      <p className="text-sm font-medium text-slate-900">
                        No inventory data
                      </p>

                      <p className="mt-1 text-xs text-slate-500">
                        Inventory will appear here once stock transactions are recorded.
                      </p>

                    </div>

                  )}

                </div>

              </section>

            </div>
          </>
        )}

      </div>

    </div>
  );
}


export default DashboardPage;