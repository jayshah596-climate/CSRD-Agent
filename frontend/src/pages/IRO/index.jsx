import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { PlusIcon, TrashIcon, ExclamationTriangleIcon } from "@heroicons/react/24/outline";
import { iroAPI } from "../../api/client";
import toast from "react-hot-toast";

const IRO_TYPES = ["impact", "risk", "opportunity"];
const RISK_TYPES = [
  "physical_acute", "physical_chronic",
  "transition_policy", "transition_technology",
  "transition_market", "transition_reputational", "systemic",
];
const TIME_HORIZONS = ["short", "medium", "long"];

export default function IROPage() {
  const { projectId } = useParams();
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    iro_type: "risk",
    risk_type: "physical_acute",
    title: "",
    description: "",
    esrs_standard: "E1",
    likelihood_score: 3,
    magnitude_score: 3,
    velocity_score: 3,
    financial_impact_min: "",
    financial_impact_max: "",
    time_horizon: "medium",
    is_climate_related: true,
    current_controls: "",
  });

  const { data: iros = [], isLoading } = useQuery({
    queryKey: ["iro", projectId],
    queryFn: () => iroAPI.list(projectId).then((r) => r.data),
  });

  const { data: summary } = useQuery({
    queryKey: ["iro-summary", projectId],
    queryFn: () => iroAPI.summary(projectId).then((r) => r.data),
  });

  const createMutation = useMutation({
    mutationFn: (data) => iroAPI.create(projectId, data),
    onSuccess: () => {
      qc.invalidateQueries(["iro", projectId]);
      qc.invalidateQueries(["iro-summary", projectId]);
      setShowForm(false);
      toast.success("IRO added");
    },
    onError: () => toast.error("Failed to add IRO"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => iroAPI.delete(projectId, id),
    onSuccess: () => {
      qc.invalidateQueries(["iro", projectId]);
      toast.success("IRO deleted");
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    createMutation.mutate({
      ...form,
      likelihood_score: parseFloat(form.likelihood_score),
      magnitude_score: parseFloat(form.magnitude_score),
      velocity_score: parseFloat(form.velocity_score),
      financial_impact_min: form.financial_impact_min ? parseFloat(form.financial_impact_min) : null,
      financial_impact_max: form.financial_impact_max ? parseFloat(form.financial_impact_max) : null,
    });
  };

  const typeColors = { impact: "badge-blue", risk: "badge-red", opportunity: "badge-green" };
  const riskColors = { physical_acute: "bg-red-100 text-red-700", physical_chronic: "bg-orange-100 text-orange-700",
    transition_policy: "bg-purple-100 text-purple-700", transition_technology: "bg-blue-100 text-blue-700",
    transition_market: "bg-yellow-100 text-yellow-700", transition_reputational: "bg-pink-100 text-pink-700",
    systemic: "bg-gray-100 text-gray-700" };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">IRO Analysis</h1>
          <p className="text-gray-500 text-sm mt-1">Map Impacts, Risks, and Opportunities per TCFD/ESRS</p>
        </div>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          <PlusIcon className="h-4 w-4 mr-2" />
          Add IRO
        </button>
      </div>

      {/* Summary */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "Total IROs", value: summary.total, color: "blue" },
            { label: "Risks", value: summary.by_type?.risk || 0, color: "red" },
            { label: "Impacts", value: summary.by_type?.impact || 0, color: "orange" },
            { label: "Opportunities", value: summary.by_type?.opportunity || 0, color: "green" },
          ].map((s) => (
            <div key={s.label} className="card text-center">
              <p className="text-2xl font-bold text-gray-900">{s.value}</p>
              <p className="text-xs text-gray-500 mt-1">{s.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Financial exposure */}
      {summary?.financial_exposure?.max > 0 && (
        <div className="card bg-red-50 border-red-100">
          <h3 className="font-semibold text-red-800 mb-1">Estimated Financial Exposure</h3>
          <p className="text-sm text-red-700">
            EUR {summary.financial_exposure.min?.toLocaleString()}M – EUR {summary.financial_exposure.max?.toLocaleString()}M
          </p>
          <p className="text-xs text-red-500 mt-1">Aggregated across all material risks</p>
        </div>
      )}

      {/* Add form */}
      {showForm && (
        <div className="card border-2 border-blue-200">
          <h3 className="font-semibold text-gray-800 mb-4">New IRO Entry</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Type *</label>
              <select className="input" value={form.iro_type}
                onChange={(e) => setForm((f) => ({ ...f, iro_type: e.target.value }))}>
                {IRO_TYPES.map((t) => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
              </select>
            </div>
            {form.iro_type === "risk" && (
              <div>
                <label className="label">Risk Type</label>
                <select className="input" value={form.risk_type}
                  onChange={(e) => setForm((f) => ({ ...f, risk_type: e.target.value }))}>
                  {RISK_TYPES.map((t) => <option key={t} value={t}>{t.replace(/_/g, " ")}</option>)}
                </select>
              </div>
            )}
            <div className="md:col-span-2">
              <label className="label">Title *</label>
              <input className="input" placeholder="Short descriptive title"
                value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} required />
            </div>
            <div className="md:col-span-2">
              <label className="label">Description</label>
              <textarea className="input" rows={2} placeholder="Detailed description..."
                value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} />
            </div>
            <div>
              <label className="label">ESRS Standard</label>
              <select className="input" value={form.esrs_standard}
                onChange={(e) => setForm((f) => ({ ...f, esrs_standard: e.target.value }))}>
                {["E1","E2","E3","E4","E5","S1","S2","S3","S4","G1"].map((s) => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Time Horizon</label>
              <select className="input" value={form.time_horizon}
                onChange={(e) => setForm((f) => ({ ...f, time_horizon: e.target.value }))}>
                {TIME_HORIZONS.map((t) => <option key={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Likelihood (1–5): {form.likelihood_score}</label>
              <input type="range" min="1" max="5" step="0.5" className="w-full"
                value={form.likelihood_score}
                onChange={(e) => setForm((f) => ({ ...f, likelihood_score: e.target.value }))} />
            </div>
            <div>
              <label className="label">Magnitude (1–5): {form.magnitude_score}</label>
              <input type="range" min="1" max="5" step="0.5" className="w-full"
                value={form.magnitude_score}
                onChange={(e) => setForm((f) => ({ ...f, magnitude_score: e.target.value }))} />
            </div>
            <div>
              <label className="label">Financial Impact Min (EUR M)</label>
              <input type="number" className="input" placeholder="0"
                value={form.financial_impact_min}
                onChange={(e) => setForm((f) => ({ ...f, financial_impact_min: e.target.value }))} />
            </div>
            <div>
              <label className="label">Financial Impact Max (EUR M)</label>
              <input type="number" className="input" placeholder="0"
                value={form.financial_impact_max}
                onChange={(e) => setForm((f) => ({ ...f, financial_impact_max: e.target.value }))} />
            </div>
            <div className="md:col-span-2">
              <label className="label">Current Controls</label>
              <input className="input" placeholder="Existing risk controls / mitigations"
                value={form.current_controls}
                onChange={(e) => setForm((f) => ({ ...f, current_controls: e.target.value }))} />
            </div>
            <div className="md:col-span-2 flex gap-3">
              <button type="button" className="btn-secondary flex-1" onClick={() => setShowForm(false)}>Cancel</button>
              <button type="submit" className="btn-primary flex-1" disabled={createMutation.isPending}>
                {createMutation.isPending ? "Saving..." : "Add IRO"}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* IRO list */}
      <div className="space-y-3">
        {isLoading ? (
          <div className="text-center py-8 text-gray-400">Loading...</div>
        ) : iros.length === 0 ? (
          <div className="card py-12 text-center">
            <ExclamationTriangleIcon className="h-8 w-8 text-gray-300 mx-auto mb-2" />
            <p className="text-gray-400 text-sm">No IROs added yet. Click "Add IRO" to start mapping.</p>
          </div>
        ) : (
          iros.map((iro) => (
            <div key={iro.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3 flex-1">
                  <div className="flex flex-col gap-1 shrink-0">
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize ${typeColors[iro.iro_type] || "badge-gray"}`}>
                      {iro.iro_type}
                    </span>
                    {iro.risk_type && (
                      <span className={`text-xs px-2 py-0.5 rounded-full ${riskColors[iro.risk_type] || "bg-gray-100 text-gray-600"}`}>
                        {iro.risk_type.replace(/_/g, " ")}
                      </span>
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-semibold text-gray-900">{iro.title}</h4>
                      {iro.is_material && <span className="badge-green text-xs">Material</span>}
                    </div>
                    {iro.description && <p className="text-sm text-gray-500 mt-1">{iro.description}</p>}
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                      <span>Score: <strong className="text-gray-700">{iro.overall_score?.toFixed(0)}/100</strong></span>
                      {iro.time_horizon && <span>Horizon: {iro.time_horizon}</span>}
                      {iro.esrs_standard && <span>ESRS: {iro.esrs_standard}</span>}
                      {iro.financial_impact_max && (
                        <span>Financial: EUR {iro.financial_impact_min}–{iro.financial_impact_max}M</span>
                      )}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => deleteMutation.mutate(iro.id)}
                  className="text-red-400 hover:text-red-600 ml-2 shrink-0"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
