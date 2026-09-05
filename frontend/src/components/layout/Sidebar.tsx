import {
  BarChart3,
  Boxes,
  Building2,
  ClipboardList,
  LayoutDashboard,
  Package,
  Settings,
  ShoppingCart,
  Truck,
  Users,
  Warehouse,
} from "lucide-react";
import { NavLink } from "react-router";

const navigation = [
  {
    label: "Dashboard",
    path: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    label: "Sales",
    path: "/sales",
    icon: ShoppingCart,
  },
  {
    label: "Purchases",
    path: "/purchases",
    icon: Truck,
  },
  {
    label: "Inventory",
    path: "/inventory",
    icon: Boxes,
  },
  {
    label: "Products",
    path: "/products",
    icon: Package,
  },
  {
    label: "Categories",
    path: "/categories",
    icon: ClipboardList,
  },
  {
    label: "Warehouses",
    path: "/warehouses",
    icon: Warehouse,
  },
  {
    label: "Customers",
    path: "/customers",
    icon: Users,
  },
  {
    label: "Suppliers",
    path: "/suppliers",
    icon: Building2,
  },
];

const intelligenceNavigation = [
  {
    label: "Intelligence",
    path: "/intelligence",
    icon: BarChart3,
  },
];

const settingsNavigation = [
  {
    label: "Settings",
    path: "/settings",
    icon: Settings,
  },
];

function NavigationItem({
  label,
  path,
  icon: Icon,
}: {
  label: string;
  path: string;
  icon: typeof LayoutDashboard;
}) {
  return (
    <NavLink
      to={path}
      className={({ isActive }) =>
        [
          "flex w-full items-center gap-3 rounded-lg px-3 py-2.5",
          "text-left text-sm font-medium transition-colors",
          isActive
            ? "bg-slate-900 text-white"
            : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
        ].join(" ")
      }
    >
      <Icon className="h-4.5 w-4.5 shrink-0" />
      <span>{label}</span>
    </NavLink>
  );
}

function Sidebar() {
  return (
    <aside className="hidden h-screen w-64 shrink-0 border-r border-slate-200 bg-white lg:flex lg:flex-col">
      <div className="flex h-16 items-center border-b border-slate-200 px-5">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-900 text-sm font-bold text-white">
            SI
          </div>

          <div>
            <p className="text-sm font-semibold text-slate-900">
              SME Intelligence
            </p>

            <p className="text-xs text-slate-500">
              Business Platform
            </p>
          </div>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-5">
        <p className="px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          Workspace
        </p>

        <div className="mt-2 space-y-1">
          {navigation.map((item) => (
            <NavigationItem
              key={item.label}
              label={item.label}
              path={item.path}
              icon={item.icon}
            />
          ))}
        </div>

        <p className="mt-8 px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          Intelligence
        </p>

        <div className="mt-2 space-y-1">
          {intelligenceNavigation.map((item) => (
            <NavigationItem
              key={item.label}
              label={item.label}
              path={item.path}
              icon={item.icon}
            />
          ))}
        </div>

        <p className="mt-8 px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          System
        </p>

        <div className="mt-2 space-y-1">
          {settingsNavigation.map((item) => (
            <NavigationItem
              key={item.label}
              label={item.label}
              path={item.path}
              icon={item.icon}
            />
          ))}
        </div>
      </nav>

      <div className="border-t border-slate-200 p-4">
        <div className="flex items-center gap-3 rounded-lg bg-slate-50 p-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-200 text-sm font-semibold text-slate-700">
            DW
          </div>

          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-slate-900">
              Administrator
            </p>

            <p className="truncate text-xs text-slate-500">
              Business Owner
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;