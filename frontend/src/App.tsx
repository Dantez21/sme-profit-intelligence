import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router";
import AppShell from "./components/layout/AppShell";
import DashboardPage from "./pages/DashboardPage";
import PlaceholderPage from "./pages/PlaceholderPage";

function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route
            path="/"
            element={<Navigate to="/dashboard" replace />}
          />

          <Route
            path="/dashboard"
            element={<DashboardPage />}
          />

          <Route
            path="/sales"
            element={
              <PlaceholderPage
                title="Sales"
                description="Manage sales transactions and customer orders."
              />
            }
          />

          <Route
            path="/purchases"
            element={
              <PlaceholderPage
                title="Purchases"
                description="Manage suppliers, purchases, and incoming stock."
              />
            }
          />

          <Route
            path="/inventory"
            element={
              <PlaceholderPage
                title="Inventory"
                description="Monitor stock levels, warehouse balances, and inventory movements."
              />
            }
          />

          <Route
            path="/products"
            element={
              <PlaceholderPage
                title="Products"
                description="Manage products, pricing, categories, and reorder levels."
              />
            }
          />

          <Route
            path="/categories"
            element={
              <PlaceholderPage
                title="Categories"
                description="Manage product categories."
              />
            }
          />

          <Route
            path="/warehouses"
            element={
              <PlaceholderPage
                title="Warehouses"
                description="Manage warehouses and storage locations."
              />
            }
          />

          <Route
            path="/customers"
            element={
              <PlaceholderPage
                title="Customers"
                description="Manage customers and their sales history."
              />
            }
          />

          <Route
            path="/suppliers"
            element={
              <PlaceholderPage
                title="Suppliers"
                description="Manage suppliers and purchasing activity."
              />
            }
          />

          <Route
            path="/intelligence"
            element={
              <PlaceholderPage
                title="Intelligence"
                description="Analyze profitability, inventory, and business performance."
              />
            }
          />

          <Route
            path="/settings"
            element={
              <PlaceholderPage
                title="Settings"
                description="Configure your business and application preferences."
              />
            }
          />

          <Route
            path="*"
            element={<Navigate to="/dashboard" replace />}
          />
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}

export default App;