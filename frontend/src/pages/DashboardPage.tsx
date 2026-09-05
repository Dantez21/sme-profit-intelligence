function DashboardPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <div>
        <p className="text-sm font-medium text-slate-500">
          Overview
        </p>

        <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          Dashboard
        </h1>

        <p className="mt-2 max-w-2xl text-sm text-slate-500">
          Monitor your business performance, inventory, sales, and profitability.
        </p>
      </div>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm font-medium text-slate-500">
            Revenue
          </p>

          <p className="mt-3 text-2xl font-bold text-slate-900">
            KES 0.00
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm font-medium text-slate-500">
            Gross Profit
          </p>

          <p className="mt-3 text-2xl font-bold text-slate-900">
            KES 0.00
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm font-medium text-slate-500">
            Gross Margin
          </p>

          <p className="mt-3 text-2xl font-bold text-slate-900">
            0.00%
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm font-medium text-slate-500">
            Stock Value
          </p>

          <p className="mt-3 text-2xl font-bold text-slate-900">
            KES 0.00
          </p>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;
