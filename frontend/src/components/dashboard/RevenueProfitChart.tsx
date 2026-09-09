import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { RevenueTrend } from "../../types/intelligence";

interface RevenueProfitChartProps {
  data: RevenueTrend[];
}

function formatAmount(value: number) {
  return new Intl.NumberFormat("en-KE", {
    style: "currency",
    currency: "KES",
    maximumFractionDigits: 0,
  }).format(value);
}

function RevenueProfitChart({
  data,
}: RevenueProfitChartProps) {
  const chartData = data.map((item) => ({
    period: item.period,
    revenue: Number(item.revenue),
    grossProfit: Number(item.gross_profit),
  }));

  if (chartData.length === 0) {
    return (
      <div className="flex min-h-80 items-center justify-center px-6">
        <div className="text-center">
          <p className="text-sm font-semibold text-slate-900">
            No trend data yet
          </p>

          <p className="mt-1 text-sm text-slate-500">
            Revenue and profit trends will appear once
            submitted sales are recorded.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-80 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{
            top: 10,
            right: 16,
            left: 8,
            bottom: 8,
          }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            vertical={false}
          />

          <XAxis
            dataKey="period"
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12 }}
          />

          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12 }}
            tickFormatter={formatAmount}
          />

          <Tooltip
            formatter={(value) =>
              formatAmount(Number(value))
            }
          />

          <Legend />

          <Line
            type="monotone"
            dataKey="revenue"
            name="Revenue"
            strokeWidth={2}
            dot={{ r: 3 }}
          />

          <Line
            type="monotone"
            dataKey="grossProfit"
            name="Gross Profit"
            strokeWidth={2}
            dot={{ r: 3 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default RevenueProfitChart;
