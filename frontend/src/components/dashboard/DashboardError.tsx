interface DashboardErrorProps {
  message?: string;
  onRetry: () => void;
}

function DashboardError({
  message = "We couldn't load the dashboard data.",
  onRetry,
}: DashboardErrorProps) {
  return (
    <div
      role="alert"
      className="rounded-xl border border-red-200 bg-red-50 p-5"
    >
      <h2 className="text-sm font-semibold text-red-900">
        Dashboard unavailable
      </h2>

      <p className="mt-1 text-sm text-red-700">
        {message}
      </p>

      <button
        type="button"
        onClick={onRetry}
        className="mt-4 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
      >
        Try again
      </button>
    </div>
  );
}

export default DashboardError;
