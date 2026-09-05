interface PlaceholderPageProps {
  title: string;
  description: string;
}

function PlaceholderPage({
  title,
  description,
}: PlaceholderPageProps) {
  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <p className="text-sm font-medium text-slate-500">
        Workspace
      </p>

      <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900">
        {title}
      </h1>

      <p className="mt-2 text-sm text-slate-500">
        {description}
      </p>

      <div className="mt-8 rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center">
        <p className="text-sm text-slate-500">
          This page is part of the application architecture and will be implemented next.
        </p>
      </div>
    </div>
  );
}

export default PlaceholderPage;
