import { useNavigate } from "react-router";
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import ProductForm from "../components/products/ProductForm";
import {
  createProduct,
  type ProductCreate,
} from "../services/products";

function CreateProductPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState("");

  const mutation = useMutation({
    mutationFn: (data: ProductCreate) => createProduct(data),

    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: ["products"],
      });

      navigate("/products");
    },

    onError: (mutationError) => {
      setError(
        mutationError instanceof Error
          ? mutationError.message
          : "Unable to create product.",
      );
    },
  });

  return (
    <div className="mx-auto max-w-4xl px-4 py-6 sm:px-6 lg:px-8">
      <div className="mb-6">
        <p className="text-sm font-medium text-slate-500">
          Products
        </p>

        <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          Add Product
        </h1>

        <p className="mt-2 text-sm text-slate-500">
          Create a product that can be used across inventory,
          purchasing, sales, and business intelligence.
        </p>
      </div>

      <ProductForm
        onSubmit={(data) => {
          setError("");
          mutation.mutate(data);
        }}
        isSubmitting={mutation.isPending}
        error={error}
      />
    </div>
  );
}

export default CreateProductPage;
