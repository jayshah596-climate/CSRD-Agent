import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { projectsAPI } from "../../api/client";
import toast from "react-hot-toast";

const ESRS_STANDARDS = [
  { id: "E1", label: "E1 – Climate Change", category: "Environmental" },
  { id: "E2", label: "E2 – Pollution", category: "Environmental" },
  { id: "E3", label: "E3 – Water and Marine Resources", category: "Environmental" },
  { id: "E4", label: "E4 – Biodiversity and Ecosystems", category: "Environmental" },
  { id: "E5", label: "E5 – Resource Use and Circular Economy", category: "Environmental" },
  { id: "S1", label: "S1 – Own Workforce", category: "Social" },
  { id: "S2", label: "S2 – Value Chain Workers", category: "Social" },
  { id: "S3", label: "S3 – Affected Communities", category: "Social" },
  { id: "S4", label: "S4 – Consumers and End-Users", category: "Social" },
  { id: "G1", label: "G1 – Business Conduct", category: "Governance" },
];

export default function NewProject() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [form, setForm] = useState({
    name: "",
    description: "",
    reporting_year: new Date().getFullYear(),
    esrs_standards: ["E1", "S1", "G1"],
  });

  const mutation = useMutation({
    mutationFn: (data) => projectsAPI.create(data),
    onSuccess: (res) => {
      qc.invalidateQueries(["projects"]);
      toast.success("Project created successfully!");
      navigate(`/projects/${res.data.id}`);
    },
    onError: (err) => toast.error(err.response?.data?.detail || "Failed to create project"),
  });

  const toggleStandard = (id) => {
    setForm((f) => ({
      ...f,
      esrs_standards: f.esrs_standards.includes(id)
        ? f.esrs_standards.filter((s) => s !== id)
        : [...f.esrs_standards, id],
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.name.trim()) return toast.error("Project name is required");
    mutation.mutate(form);
  };

  const groupedStandards = ESRS_STANDARDS.reduce((acc, s) => {
    if (!acc[s.category]) acc[s.category] = [];
    acc[s.category].push(s);
    return acc;
  }, {});

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">New Project</h1>
        <p className="text-gray-500 text-sm mt-1">Set up a new CSRD reporting project</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="card space-y-4">
          <h2 className="font-semibold text-gray-800">Basic Information</h2>
          <div>
            <label className="label">Project Name *</label>
            <input
              className="input"
              placeholder="e.g., CSRD Report 2024 – Acme Corp"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              required
            />
          </div>
          <div>
            <label className="label">Description</label>
            <textarea
              className="input"
              rows={2}
              placeholder="Optional description..."
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            />
          </div>
          <div>
            <label className="label">Reporting Year *</label>
            <select
              className="input"
              value={form.reporting_year}
              onChange={(e) => setForm((f) => ({ ...f, reporting_year: parseInt(e.target.value) }))}
            >
              {[2022, 2023, 2024, 2025, 2026].map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="card space-y-4">
          <div>
            <h2 className="font-semibold text-gray-800">ESRS Standards</h2>
            <p className="text-xs text-gray-500 mt-1">
              Select which ESRS standards apply to your organisation (based on Double Materiality Assessment)
            </p>
          </div>

          {Object.entries(groupedStandards).map(([category, standards]) => (
            <div key={category}>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">{category}</p>
              <div className="space-y-2">
                {standards.map((s) => (
                  <label
                    key={s.id}
                    className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                      form.esrs_standards.includes(s.id)
                        ? "border-blue-500 bg-blue-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={form.esrs_standards.includes(s.id)}
                      onChange={() => toggleStandard(s.id)}
                      className="h-4 w-4 text-blue-600 rounded"
                    />
                    <span className="text-sm font-medium text-gray-800">{s.label}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="flex gap-3">
          <button
            type="button"
            className="btn-secondary flex-1"
            onClick={() => navigate("/projects")}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn-primary flex-1"
            disabled={mutation.isPending}
          >
            {mutation.isPending ? "Creating..." : "Create Project"}
          </button>
        </div>
      </form>
    </div>
  );
}
