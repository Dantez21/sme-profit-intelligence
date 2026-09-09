export function formatCurrency(
  value: string | number,
): string {
  const amount =
    typeof value === "number"
      ? value
      : Number(value);

  if (!Number.isFinite(amount)) {
    return "KES 0.00";
  }

  return new Intl.NumberFormat("en-KE", {
    style: "currency",
    currency: "KES",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatPercentage(
  value: string | number,
): string {
  const percentage =
    typeof value === "number"
      ? value
      : Number(value);

  if (!Number.isFinite(percentage)) {
    return "0.00%";
  }

  return `${percentage.toFixed(2)}%`;
}

export function formatQuantity(
  value: string | number,
  decimals = 3,
): string {
  const quantity =
    typeof value === "number"
      ? value
      : Number(value);

  if (!Number.isFinite(quantity)) {
    return "0.000";
  }

  return quantity.toFixed(decimals);
}
