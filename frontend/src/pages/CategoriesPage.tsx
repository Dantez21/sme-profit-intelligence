import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Pencil, Plus, Search, Trash2 } from "lucide-react";
import { useMemo, useState } from "react";

import {
  createCategory,
  deleteCategory,
  getCategories,
  updateCategory,
} from "../services/categories";
import type { Category } from "../types/category";

interface CategoryFormState {
  name: string;
  description: string;
}

const emptyForm: CategoryFormState = {
  name: "",
  description: "",
};

function CategoriesPage() {
  const queryClient = useQueryClient();

  const [search, setSearch] = useState("");
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingCategory, setEditingCategory] =
    useState<Category | null>(null);
  const [form, setForm] = useState<CategoryFormState>(emptyForm);
  const [formError, setFormError] = useState("");

  const categoriesQuery = useQuery({
    queryKey: ["categories"],
    queryFn: getCategories,
  });

  const filteredCategories = useMemo(() => {
    const categories = categoriesQuery.data ?? [];
    const term = search.trim().toLowerCase();

    if (!term) {
      return categories;
    }

    return categories.filter(
      (category) =>
        category.name.toLowerCase().includes(term) ||
        category.description?.toLowerCase().includes(term),
    );
  }, [categoriesQuery.data, search]);

  const createMutation = useMutation({
    mutationFn: createCategory,

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["categories"],
      });

      closeForm();
    },

    onError: (error) => {
      setFormError(
        error instanceof Error
          ? error.message
          : "Unable to create category.",
      );
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({
      categoryId,
      data,
    }: {
      categoryId: number;
      data: CategoryFormState;
    }) => updateCategory(categoryId, data),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["categories"],
      });

      closeForm();
    },

    onError: (error) => {
      setFormError(
        error instanceof Error
          ? error.message
          : "Unable to update category.",
      );
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteCategory,

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["categories"],
      });
    },

    onError: (error) => {
      window.alert(
        error instanceof Error
          ? error.message
          : "Unable to delete category.",
      );
    },
  });

  function closeForm() {
    setIsFormOpen(false);
    setEditingCategory(null);
    setForm(emptyForm);
    setFormError("");
  }

  function openCreateForm() {
    setEditingCategory(null);
    setForm(emptyForm);
    setFormError("");
    setIsFormOpen(true);
  }

  function openEditForm(category: Category) {
    setEditingCategory(category);
    setForm({
      name: category.name,
      description: category.description ?? "",
    });
    setFormError("");
    setIsFormOpen(true);
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError("");

    const data = {
      name: form.name.trim(),
      description: form.description.trim() || undefined,
    };

    if (editingCategory) {
      updateMutation.mutate({
        categoryId: editingCategory.id,
        data: {
          name: data.name,
          description: data.description ?? "",
        },
      });

      return;
    }

    createMutation.mutate(data);
  }

  function handleDelete(category: Category) {
    const confirmed = window.confirm(
      `Delete "${category.name}"?\n\nCategories assigned to products cannot be deleted.`,
    );

    if (!confirmed) {
      return;
    }

    deleteMutation.mutate(category.id);
  }

  const isSaving =
    createMutation.isPending ||
    updateMutation.isPending;

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">
            Catalogue
          </p>

          <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            Categories
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            Organize your products into clear business categories.
          </p>
        </div>

        <button
          type="button"
          onClick={openCreateForm}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          <Plus className="h-4 w-4" />
          Add Category
        </button>
      </div>

      {isFormOpen && (
        <section className="mt-6 rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-5 py-4">
            <h2 className="font-semibold text-slate-900">
              {editingCategory
                ? "Edit Category"
                : "Create Category"}
            </h2>

            <p className="mt-1 text-xs text-slate-500">
              {editingCategory
                ? "Update the category information."
                : "Create a category for organizing products."}
            </p>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="grid gap-5 p-5">
              <div>
                <label
                  htmlFor="category-name"
                  className="block text-sm font-medium text-slate-700"
                >
                  Category Name
                </label>

                <input
                  id="category-name"
                  required
                  minLength={2}
                  maxLength={100}
                  value={form.name}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      name: event.target.value,
                    }))
                  }
                  placeholder="e.g. Beef Cuts"
                  className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:ring-1 focus:ring-slate-900"
                />
              </div>

              <div>
                <label
                  htmlFor="category-description"
                  className="block text-sm font-medium text-slate-700"
                >
                  Description
                </label>

                <textarea
                  id="category-description"
                  maxLength={255}
                  rows={3}
                  value={form.description}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      description: event.target.value,
                    }))
                  }
                  placeholder="Optional description..."
                  className="mt-1.5 w-full resize-none rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-slate-900 focus:ring-1 focus:ring-slate-900"
                />
              </div>
            </div>

            {formError && (
              <div
                role="alert"
                className="mx-5 mb-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
              >
                {formError}
              </div>
            )}

            <div className="flex justify-end gap-3 border-t border-slate-200 px-5 py-4">
              <button
                type="button"
                onClick={closeForm}
                disabled={isSaving}
                className="rounded-lg border border-slate-300 px-4 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
              >
                Cancel
              </button>

              <button
                type="submit"
                disabled={isSaving}
                className="rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isSaving
                  ? "Saving..."
                  : editingCategory
                    ? "Save Changes"
                    : "Create Category"}
              </button>
            </div>
          </form>
        </section>
      )}

      <div className="mt-6 rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 p-4">
          <div className="flex max-w-md items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 focus-within:border-slate-400 focus-within:bg-white">
            <Search className="h-4 w-4 shrink-0 text-slate-400" />

            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search categories..."
              aria-label="Search categories"
              className="w-full bg-transparent text-sm text-slate-900 outline-none placeholder:text-slate-400"
            />
          </div>
        </div>

        {categoriesQuery.isLoading && (
          <div className="p-8 text-center text-sm text-slate-500">
            Loading categories...
          </div>
        )}

        {categoriesQuery.isError && (
          <div
            role="alert"
            className="p-8 text-center"
          >
            <p className="text-sm font-semibold text-red-700">
              Unable to load categories
            </p>

            <p className="mt-1 text-sm text-slate-500">
              Please check that the BizNuru API is available.
            </p>

            <button
              type="button"
              onClick={() => void categoriesQuery.refetch()}
              className="mt-4 rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              Try Again
            </button>
          </div>
        )}

        {!categoriesQuery.isLoading &&
          !categoriesQuery.isError &&
          filteredCategories.length === 0 && (
            <div className="p-10 text-center">
              <p className="text-sm font-semibold text-slate-900">
                No categories found
              </p>

              <p className="mt-1 text-sm text-slate-500">
                {search
                  ? "Try a different search."
                  : "Create your first category to organize products."}
              </p>

              {!search && (
                <button
                  type="button"
                  onClick={openCreateForm}
                  className="mt-4 inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
                >
                  <Plus className="h-4 w-4" />
                  Add Your First Category
                </button>
              )}
            </div>
          )}

        {!categoriesQuery.isLoading &&
          !categoriesQuery.isError &&
          filteredCategories.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[650px]">
                <caption className="sr-only">
                  Product categories
                </caption>

                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50/70">
                    <th
                      scope="col"
                      className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500"
                    >
                      Category
                    </th>

                    <th
                      scope="col"
                      className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500"
                    >
                      Description
                    </th>

                    <th
                      scope="col"
                      className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500"
                    >
                      Actions
                    </th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-slate-100">
                  {filteredCategories.map((category) => (
                    <tr
                      key={category.id}
                      className="transition hover:bg-slate-50"
                    >
                      <td className="px-5 py-4">
                        <p className="text-sm font-medium text-slate-900">
                          {category.name}
                        </p>
                      </td>

                      <td className="px-5 py-4">
                        <p className="max-w-lg truncate text-sm text-slate-600">
                          {category.description || "—"}
                        </p>
                      </td>

                      <td className="px-5 py-4">
                        <div className="flex justify-end gap-2">
                          <button
                            type="button"
                            onClick={() => openEditForm(category)}
                            aria-label={`Edit ${category.name}`}
                            className="rounded-lg p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
                          >
                            <Pencil className="h-4 w-4" />
                          </button>

                          <button
                            type="button"
                            onClick={() => handleDelete(category)}
                            disabled={deleteMutation.isPending}
                            aria-label={`Delete ${category.name}`}
                            className="rounded-lg p-2 text-slate-500 transition hover:bg-red-50 hover:text-red-600 disabled:opacity-50"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
      </div>

      {!categoriesQuery.isLoading &&
        !categoriesQuery.isError &&
        filteredCategories.length > 0 && (
          <div className="mt-3 px-1 text-xs text-slate-500">
            Showing {filteredCategories.length}{" "}
            {filteredCategories.length === 1
              ? "category"
              : "categories"}
          </div>
        )}
    </div>
  );
}

export default CategoriesPage;