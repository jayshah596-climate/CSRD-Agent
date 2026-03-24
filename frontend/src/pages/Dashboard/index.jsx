import React from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  FolderIcon,
  CloudIcon,
  ChartBarIcon,
  DocumentTextIcon,
  ArrowRightIcon,
  PlusIcon,
} from "@heroicons/react/24/outline";
import { projectsAPI } from "../../api/client";
import useAuthStore from "../../store/authStore";

export default function Dashboard() {
  const user = useAuthStore((s) => s.user);
  const { data: projects = [], isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: () => projectsAPI.list().then((r) => r.data),
  });

  const stats = [
    { label: "Active Projects", value: projects.filter((p) => p.status !== "archived").length, icon: FolderIcon, color: "blue" },
    { label: "Reports Generated", value: 0, icon: DocumentTextIcon, color: "green" },
    { label: "GHG Analyses", value: projects.filter((p) => p.emissions_complete).length, icon: CloudIcon, color: "orange" },
    { label: "Materiality Done", value: projects.filter((p) => p.materiality_complete).length, icon: ChartBarIcon, color: "purple" },
  ];

  const colorMap = {
    blue: "bg-blue-50 text-blue-600",
    green: "bg-green-50 text-green-600",
    orange: "bg-orange-50 text-orange-600",
    purple: "bg-purple-50 text-purple-600",
  };

  return (
    <div className="space-y-6">
      {/* Welcome banner */}
      <div className="bg-gradient-to-r from-blue-900 to-blue-800 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Welcome back, {user?.full_name?.split(" ")[0]}! 👋</h1>
            <p className="text-blue-200 mt-1 text-sm">
              Your CSRD/ESRS 2025 reporting platform. Manage projects, assess materiality, and generate compliant reports.
            </p>
          </div>
          <Link
            to="/projects/new"
            className="hidden md:flex items-center gap-2 bg-white text-blue-900 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-50 transition-colors"
          >
            <PlusIcon className="h-4 w-4" />
            New Project
          </Link>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="card">
            <div className="flex items-center gap-4">
              <div className={`h-10 w-10 rounded-lg flex items-center justify-center ${colorMap[stat.color]}`}>
                <stat.icon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <p className="text-xs text-gray-500">{stat.label}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Projects list */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Recent Projects</h2>
          <Link to="/projects" className="text-sm text-blue-700 hover:text-blue-800 flex items-center gap-1">
            View all <ArrowRightIcon className="h-4 w-4" />
          </Link>
        </div>

        {isLoading ? (
          <div className="py-8 text-center text-gray-400 text-sm">Loading projects...</div>
        ) : projects.length === 0 ? (
          <div className="py-12 text-center">
            <FolderIcon className="h-10 w-10 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">No projects yet</p>
            <p className="text-gray-400 text-sm mb-4">Create your first CSRD reporting project</p>
            <Link to="/projects/new" className="btn-primary">
              <PlusIcon className="h-4 w-4 mr-2" />
              New Project
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {projects.slice(0, 5).map((p) => (
              <Link
                key={p.id}
                to={`/projects/${p.id}`}
                className="flex items-center justify-between p-4 rounded-xl border border-gray-100 hover:border-blue-200 hover:bg-blue-50/30 transition-all group"
              >
                <div className="flex items-center gap-3">
                  <div className="h-9 w-9 rounded-lg bg-blue-100 flex items-center justify-center">
                    <FolderIcon className="h-5 w-5 text-blue-700" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{p.name}</p>
                    <p className="text-xs text-gray-500">FY {p.reporting_year} · {p.esrs_standards?.join(", ")}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <StatusBadge status={p.status} />
                  <ProgressBar value={calculateProgress(p)} />
                  <ArrowRightIcon className="h-4 w-4 text-gray-300 group-hover:text-blue-500 transition-colors" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* ESRS Standards info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-3">ESRS Coverage</h3>
          <div className="space-y-2">
            {[
              { id: "E1-E5", label: "Environmental", color: "green", desc: "Climate, Pollution, Water, Biodiversity, Resources" },
              { id: "S1-S4", label: "Social", color: "blue", desc: "Workforce, Value Chain, Communities, Consumers" },
              { id: "G1", label: "Governance", color: "purple", desc: "Business Conduct, Anti-Corruption" },
            ].map((item) => (
              <div key={item.id} className="flex items-start gap-3">
                <span className={`mt-0.5 h-2 w-2 rounded-full bg-${item.color}-500 shrink-0`} />
                <div>
                  <p className="text-sm font-medium text-gray-800">{item.id} – {item.label}</p>
                  <p className="text-xs text-gray-500">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-3">Platform Capabilities</h3>
          <div className="space-y-2">
            {[
              "Double Materiality Assessment (DMA)",
              "GHG Scope 1, 2, 3 Calculations",
              "NGFS Climate Scenario Analysis",
              "IRO (Impacts, Risks, Opportunities)",
              "AI-Powered ESRS Narratives",
              "XBRL Digital Filing Export",
            ].map((cap) => (
              <div key={cap} className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                <span className="text-sm text-gray-700">{cap}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }) {
  const map = {
    draft: "badge-gray",
    in_progress: "badge-blue",
    review: "badge-yellow",
    completed: "badge-green",
    archived: "badge-gray",
  };
  return <span className={map[status] || "badge-gray"}>{status?.replace("_", " ")}</span>;
}

function ProgressBar({ value }) {
  return (
    <div className="hidden sm:flex items-center gap-2">
      <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-600 rounded-full transition-all"
          style={{ width: `${value}%` }}
        />
      </div>
      <span className="text-xs text-gray-400">{value}%</span>
    </div>
  );
}

function calculateProgress(p) {
  const steps = [
    p.data_collection_complete,
    p.materiality_complete,
    p.iro_complete,
    p.emissions_complete,
    p.scenario_complete,
    p.narrative_complete,
  ];
  const done = steps.filter(Boolean).length;
  return Math.round((done / steps.length) * 100);
}
