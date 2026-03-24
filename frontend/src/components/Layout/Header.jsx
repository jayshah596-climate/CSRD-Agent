import React from "react";
import { useNavigate } from "react-router-dom";
import { Bars3Icon, BellIcon, ArrowRightOnRectangleIcon } from "@heroicons/react/24/outline";
import useAuthStore from "../../store/authStore";
import toast from "react-hot-toast";

export default function Header({ onMenuClick }) {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    toast.success("Logged out successfully");
    navigate("/login");
  };

  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shrink-0">
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-1.5 rounded-lg hover:bg-gray-100 text-gray-500"
        >
          <Bars3Icon className="h-5 w-5" />
        </button>
        <div className="hidden lg:block">
          <p className="text-sm text-gray-500">
            CSRD/ESRS 2025 Reporting Platform
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Subscription badge */}
        <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${
          user?.subscription_tier === "enterprise"
            ? "bg-purple-100 text-purple-800"
            : user?.subscription_tier === "pro"
            ? "bg-blue-100 text-blue-800"
            : "bg-gray-100 text-gray-600"
        }`}>
          {user?.subscription_tier?.toUpperCase() || "FREE"}
        </span>

        {/* Notification bell */}
        <button className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500 relative">
          <BellIcon className="h-5 w-5" />
        </button>

        {/* User avatar + logout */}
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-blue-900 flex items-center justify-center text-white text-sm font-semibold">
            {user?.full_name?.[0]?.toUpperCase() || "U"}
          </div>
          <span className="hidden md:block text-sm font-medium text-gray-700">
            {user?.full_name}
          </span>
        </div>

        <button
          onClick={handleLogout}
          className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500"
          title="Logout"
        >
          <ArrowRightOnRectangleIcon className="h-5 w-5" />
        </button>
      </div>
    </header>
  );
}
