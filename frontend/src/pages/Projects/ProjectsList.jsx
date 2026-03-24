import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  PlusIcon,
  FolderIcon,
  TrashIcon,
  ArrowRightIcon,
  CalendarIcon,
} from "@heroicons/react/24/outline";
import { projectsAPI } from "../../api/client";
import toast from "react-hot-toast";

export default function ProjectsList() {
  const qc = useQueryClient();
  const { data: projects = [], isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: () => projectsAPI.list().then((r) => r.data),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => projectsAPI.delete(id),
    onSuccess: () => {
      qc.invalidateQueries(["projects"]);
      toast.success("Project deleted");
    },
    onError: () => toast.error("Failed to delete project"),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
          <p className="text-gray-500 text-sm mt-1">Manage your CSRD reporting projects</p>
        </div>
        <Link to="/projects/new" className="btn-primary">
          <PlusIcon className="h-4 w-4 mr-2" />
          New Project
        </Link>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-3" />
              <div className="h-3 bg-gray-100 rounded w-1/2" />
            </div>
          ))}
        </div>
      ) : projects.length === 0 ? (
        <div className="card py-16 text-center">
          <FolderIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-700 mb-2">No projects yet</h3>
          <p className="text-gray-400 text-sm mb-6">
            Create your first CSRD reporting project to get started
          </p>
          <Link to="/projects/new" className="btn-primary">
            <PlusIcon className="h-4 w-4 mr-2" />
            Create First Project
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((p) => (
            <ProjectCard
              key={p.id}
              project={p}
              onDelete={() => {
                if (window.confirm(`Delete "${p.name}"?`)) {
                  deleteMutation.mutate(p.id);
                }
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ProjectCard({ project: p, onDelete }) {
  const progress = calculateProgress(p);

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="h-10 w-10 rounded-xl bg-blue-100 flex items-center justify-center">
          <FolderIcon className="h-5 w-5 text-blue-700" />
        </div>
        <StatusBadge status={p.status} />
      </div>

      <h3 className="font-semibold text-gray-900 mb-1">{p.name}</h3>
      {p.description && (
        <p className="text-xs text-gray-500 mb-2 line-clamp-2">{p.description}</p>
      )}

      <div className="flex items-center gap-2 text-xs text-gray-400 mb-4">
        <CalendarIcon className="h-3.5 w-3.5" />
        FY {p.reporting_year}
        <span className="text-gray-300">·</span>
        {p.esrs_standards?.join(", ")}
      </div>

      {/* Progress */}
      <div className="mb-4">
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>Progress</span>
          <span>{progress}%</span>
        </div>
        <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-600 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Step indicators */}
      <div className="flex gap-1 mb-4">
        {[
          { key: "data_collection_complete", label: "Data" },
          { key: "materiality_complete", label: "Mat" },
          { key: "emissions_complete", label: "GHG" },
          { key: "iro_complete", label: "IRO" },
          { key: "scenario_complete", label: "Scen" },
          { key: "narrative_complete", label: "Rep" },
        ].map((step) => (
          <div
            key={step.key}
            title={step.label}
            className={`flex-1 h-1.5 rounded-full ${p[step.key] ? "bg-green-500" : "bg-gray-200"}`}
          />
        ))}
      </div>

      <div className="flex items-center justify-between">
        <button
          onClick={onDelete}
          className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"
        >
          <TrashIcon className="h-4 w-4" />
        </button>
        <Link
          to={`/projects/${p.id}`}
          className="flex items-center gap-1.5 text-sm font-medium text-blue-700 hover:text-blue-800"
        >
          Open <ArrowRightIcon className="h-4 w-4" />
        </Link>
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

function calculateProgress(p) {
  const steps = [
    p.data_collection_complete, p.materiality_complete,
    p.iro_complete, p.emissions_complete,
    p.scenario_complete, p.narrative_complete,
  ];
  return Math.round(steps.filter(Boolean).length / steps.length * 100);
}
