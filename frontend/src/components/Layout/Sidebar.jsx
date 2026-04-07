import React from "react";
import { NavLink, useParams } from "react-router-dom";
import {
  HomeIcon,
  FolderIcon,
  ChartBarIcon,
  CloudIcon,
  UsersIcon,
  CogIcon,
  DocumentTextIcon,
  BeakerIcon,
  ExclamationTriangleIcon,
  GlobeAltIcon,
  XMarkIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";
import useAuthStore from "../../store/authStore";

const navItems = [
  { name: "Dashboard", href: "/dashboard", icon: HomeIcon },
  { name: "Projects", href: "/projects", icon: FolderIcon },
  { name: "CSRD Agent", href: "/agent", icon: SparklesIcon },
];

const projectNavItems = [
  { name: "Data Collection", href: "data", icon: DocumentTextIcon },
  { name: "Materiality", href: "materiality", icon: ChartBarIcon },
  { name: "Emissions (GHG)", href: "emissions", icon: CloudIcon },
  { name: "IRO Analysis", href: "iro", icon: ExclamationTriangleIcon },
  { name: "Scenarios", href: "scenarios", icon: GlobeAltIcon },
  { name: "Reports", href: "reports", icon: BeakerIcon },
];

export default function Sidebar({ open, onClose }) {
  const { projectId } = useParams();
  const user = useAuthStore((s) => s.user);

  const navLinkClass = ({ isActive }) =>
    `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
      isActive
        ? "bg-blue-900 text-white"
        : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
    }`;

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex lg:flex-col lg:w-64 lg:bg-white lg:border-r lg:border-gray-200 lg:shrink-0">
        <SidebarContent
          navItems={navItems}
          projectNavItems={projectNavItems}
          projectId={projectId}
          navLinkClass={navLinkClass}
          user={user}
        />
      </aside>

      {/* Mobile sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-30 w-64 bg-white border-r border-gray-200 transform transition-transform duration-200 ease-in-out lg:hidden ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between p-4 border-b">
          <Logo />
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-gray-100">
            <XMarkIcon className="h-5 w-5 text-gray-500" />
          </button>
        </div>
        <SidebarContent
          navItems={navItems}
          projectNavItems={projectNavItems}
          projectId={projectId}
          navLinkClass={navLinkClass}
          user={user}
        />
      </aside>
    </>
  );
}

function SidebarContent({ navItems, projectNavItems, projectId, navLinkClass, user }) {
  return (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="flex items-center gap-2 px-4 py-5 border-b border-gray-100">
        <Logo />
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink key={item.name} to={item.href} className={navLinkClass} end={item.href === "/dashboard"}>
            <item.icon className="h-5 w-5 shrink-0" />
            {item.name}
          </NavLink>
        ))}

        {/* Project-specific nav */}
        {projectId && (
          <div className="mt-6">
            <p className="px-3 mb-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
              Current Project
            </p>
            {projectNavItems.map((item) => (
              <NavLink
                key={item.name}
                to={`/projects/${projectId}/${item.href}`}
                className={navLinkClass}
              >
                <item.icon className="h-5 w-5 shrink-0" />
                {item.name}
              </NavLink>
            ))}
          </div>
        )}

        {/* Settings */}
        <div className="mt-6">
          <p className="px-3 mb-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
            Settings
          </p>
          <NavLink to="/settings/company" className={navLinkClass}>
            <CogIcon className="h-5 w-5 shrink-0" />
            Company Profile
          </NavLink>
        </div>
      </nav>

      {/* User info */}
      <div className="px-4 py-4 border-t border-gray-100">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-full bg-blue-900 flex items-center justify-center text-white text-sm font-semibold">
            {user?.full_name?.[0]?.toUpperCase() || "U"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">{user?.full_name}</p>
            <p className="text-xs text-gray-500 truncate capitalize">{user?.subscription_tier}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function Logo() {
  return (
    <div className="flex items-center gap-2">
      <div className="h-8 w-8 rounded-lg bg-blue-900 flex items-center justify-center">
        <span className="text-white font-bold text-xs">CA</span>
      </div>
      <div>
        <p className="text-sm font-bold text-gray-900">CSRD Agent</p>
        <p className="text-xs text-gray-500">ESRS 2025</p>
      </div>
    </div>
  );
}
