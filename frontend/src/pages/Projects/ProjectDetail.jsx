import React from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  DocumentTextIcon, ChartBarIcon, CloudIcon,
  ExclamationTriangleIcon, GlobeAltIcon, BeakerIcon,
  CheckCircleIcon, ArrowRightIcon,
} from "@heroicons/react/24/outline";
import { projectsAPI } from "../../api/client";

const WORKFLOW_STEPS = [
  { key: "data_collection", label: "Data Collection", desc: "Enter ESRS-required data points", icon: DocumentTextIcon, href: "data", color: "blue" },
  { key: "materiality", label: "Double Materiality", desc: "Assess impact & financial materiality", icon: ChartBarIcon, href: "materiality", color: "green" },
  { key: "emissions", label: "GHG Emissions", desc: "Calculate Scope 1, 2, 3 emissions", icon: CloudIcon, href: "emissions", color: "orange" },
  { key: "iro", label: "IRO Analysis", desc: "Map Impacts, Risks, Opportunities", icon: ExclamationTriangleIcon, href: "iro", color: "red" },
  { key: "scenario", label: "Scenario Analysis", desc: "NGFS climate scenarios & VaR", icon: GlobeAltIcon, href: "scenarios", color: "purple" },
  { key: "narrative", label: "Report Generation", desc: "AI narratives + PDF/XBRL export", icon: BeakerIcon, href: "reports", color: "teal" },
];

const colorMap = {
  blue: { bg: "bg-blue-100", text: "text-blue-600", border: "border-blue-200" },
  green: { bg: "bg-green-100", text: "text-green-600", border: "border-green-200" },
  orange: { bg: "bg-orange-100", text: "text-orange-600", border: "border-orange-200" },
  red: { bg: "bg-red-100", text: "text-red-600", border: "border-red-200" },
  purple: { bg: "bg-purple-100", text: "text-purple-600", border: "border-purple-200" },
  teal: { bg: "bg-teal-100", text: "text-teal-600", border: "border-teal-200" },
};

export default function ProjectDetail() {
  const { projectId } = useParams();

  const { data: project, isLoading } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => projectsAPI.get(projectId).then((r) => r.data),
  });

  const { data: progress } = useQuery({
    queryKey: ["project-progress", projectId],
    queryFn: () => projectsAPI.progress(projectId).then((r) => r.data),
  });

  if (isLoading) {
    return <div className="text-center py-12 text-gray-400">Loading project...</div>;
  }

  if (!project) {
    return <div className="text-center py-12 text-red-500">Project not found</div>;
  }

  const completedSteps = progress?.completed_steps || 0;
  const totalSteps = progress?.total_steps || 6;
  const progressPct = progress?.progress_pct || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
            {project.description && (
              <p className="text-gray-500 text-sm mt-1">{project.description}</p>
            )}
            <div className="flex items-center gap-3 mt-3">
              <span className="text-sm text-gray-500">FY {project.reporting_year}</span>
              <span className="text-gray-300">·</span>
              <div className="flex gap-1">
                {project.esrs_standards?.map((s) => (
                  <span key={s} className="badge-blue text-xs">{s}</span>
                ))}
              </div>
            </div>
          </div>
          <StatusBadge status={project.status} />
        </div>

        {/* Progress bar */}
        <div className="mt-5">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span className="font-medium">Overall Progress</span>
            <span>{completedSteps}/{totalSteps} steps · {progressPct}%</span>
          </div>
          <div className="w-full h-2.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-600 to-green-500 rounded-full transition-all"
              style={{ width: `${progressPct}%` }}
            />
          </div>
        </div>
      </div>

      {/* Workflow steps */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Reporting Workflow</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {WORKFLOW_STEPS.map((step, idx) => {
            const isComplete = progress?.steps?.[step.key];
            const colors = colorMap[step.color];
            const isAvailable = idx === 0 || progress?.steps?.[WORKFLOW_STEPS[idx - 1]?.key];

            return (
              <Link
                key={step.key}
                to={`/projects/${projectId}/${step.href}`}
                className={`card hover:shadow-md transition-all group relative ${
                  !isAvailable ? "opacity-60" : ""
                }`}
              >
                {isComplete && (
                  <CheckCircleIcon className="absolute top-4 right-4 h-5 w-5 text-green-500" />
                )}
                <div className={`h-10 w-10 rounded-xl ${colors.bg} flex items-center justify-center mb-3`}>
                  <step.icon className={`h-5 w-5 ${colors.text}`} />
                </div>
                <div className="flex items-center gap-1.5 mb-1">
                  <span className="text-xs text-gray-400 font-mono">Step {idx + 1}</span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-1">{step.label}</h3>
                <p className="text-xs text-gray-500 mb-3">{step.desc}</p>
                <div className="flex items-center justify-between">
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                    isComplete ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"
                  }`}>
                    {isComplete ? "Complete" : "Pending"}
                  </span>
                  <ArrowRightIcon className="h-4 w-4 text-gray-300 group-hover:text-blue-500 transition-colors" />
                </div>
              </Link>
            );
          })}
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
  };
  return <span className={map[status] || "badge-gray"}>{status?.replace("_", " ")}</span>;
}
