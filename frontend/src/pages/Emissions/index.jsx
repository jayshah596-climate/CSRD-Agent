import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { PlusIcon, TrashIcon, CloudIcon } from "@heroicons/react/24/outline";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { emissionsAPI } from "../../api/client";
import toast from "react-hot-toast";

const SCOPE_COLORS = {
  scope_1: "#1e3a5f",
  scope_2_location: "#2d6a4f",
  scope_2_market: "#4ade80",
  scope_3: "#f59e0b",
};

export default function EmissionsPage() {
  const { projectId } = useParams();
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    scope: "scope_1",
    source_name: "",
    activity_value: "",
    activity_unit: "kWh",
    emission_factor_value: "",
    emission_factor_unit: "kgCO2e/kWh",
    emission_factor_source: "DEFRA 2023",
    category: "",
    notes: "",
  });

  const { data: emissions = [], isLoading } = useQuery({
    queryKey: ["emissions", projectId],
    queryFn: () => emissionsAPI.list(projectId).then((r) => r.data),
  });

  const { data: summary } = useQuery({
    queryKey: ["emissions-summary", projectId],
    queryFn: () => emissionsAPI.summary(projectId).then((r) => r.data),
  });

  const { data: factors = [] } = useQuery({
    queryKey: ["emission-factors", projectId],
    queryFn: () => emissionsAPI.factors(projectId).then((r) => r.data),
  });

  const createMutation = useMutation({
    mutationFn: (data) => emissionsAPI.create(projectId, data),
    onSuccess: () => {
      qc.invalidateQueries(["emissions", projectId]);
      qc.invalidateQueries(["emissions-summary", projectId]);
      setShowForm(false);
      resetForm();
      toast.success("Emission entry added");
    },
    onError: (e) => toast.error(e.response?.data?.detail || "Failed to add entry"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => emissionsAPI.delete(projectId, id),
    onSuccess: () => {
      qc.invalidateQueries(["emissions", projectId]);
      qc.invalidateQueries(["emissions-summary", projectId]);
      toast.success("Entry deleted");
    },
  });

  const resetForm = () => setForm({
    scope: "scope_1", source_name: "", activity_value: "", activity_unit: "kWh",
    emission_factor_value: "", emission_factor_unit: "kgCO2e/kWh",
    emission_factor_source: "DEFRA 2023", category: "", notes: "",
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    createMutation.mutate({
      ...form,
      activity_value: parseFloat(form.activity_value),
      emission_factor_value: parseFloat(form.emission_factor_value),
    });
  };

  const chartData = summary ? [
    { name: "Scope 1", value: summary.scope_1?.total_co2e || 0, scope: "scope_1" },
    { name: "Scope 2 (loc)", value: summary.scope_2_location?.total_co2e || 0, scope: "scope_2_location" },
    { name: "Scope 2 (mkt)", value: summary.scope_2_market?.total_co2e || 0, scope: "scope_2_market" },
    { name: "Scope 3", value: summary.scope_3?.total_co2e || 0, scope: "scope_3" },
  ] : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">GHG Emissions</h1>
          <p className="text-gray-500 text-sm mt-1">Scope 1, 2, 3 calculations per ESRS E1-6 and GHG Protocol</p>
        </div>
        <button className="btn-primary" onClick={() => setShowForm(true)}>
          <PlusIcon className="h-4 w-4 mr-2" />
          Add Entry
        </button>
      </div>

      {/* Summary cards */}
      {summary && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: "Scope 1", value: summary.scope_1?.total_co2e || 0, color: "blue" },
            { label: "Scope 2 (Location)", value: summary.scope_2_location?.total_co2e || 0, color: "green" },
            { label: "Scope 3", value: summary.scope_3?.total_co2e || 0, color: "orange" },
            { label: "Total GHG", value: summary.total_co2e || 0, color: "purple" },
          ].map((s) => (
            <div key={s.label} className="card">
              <p className="text-xs text-gray-500 mb-1">{s.label}</p>
              <p className="text-2xl font-bold text-gray-900">{s.value.toLocaleString(undefined, { maximumFractionDigits: 1 })}</p>
              <p className="text-xs text-gray-400">tCO₂e</p>
            </div>
          ))}
        </div>
      )}

      {/* Chart */}
      {chartData.some((d) => d.value > 0) && (
        <div className="card">
          <h3 className="font-semibold text-gray-800 mb-4">GHG Emissions by Scope (tCO₂e)</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData} barSize={40}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip
                formatter={(v) => [`${v.toLocaleString(undefined, { maximumFractionDigits: 1 })} tCO₂e`]}
              />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {chartData.map((entry) => (
                  <Cell key={entry.scope} fill={SCOPE_COLORS[entry.scope] || "#6b7280"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Add form */}
      {showForm && (
        <div className="card border-blue-200 border-2">
          <h3 className="font-semibold text-gray-800 mb-4">Add Emission Entry</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Scope</label>
              <select className="input" value={form.scope} onChange={(e) => setForm((f) => ({ ...f, scope: e.target.value }))}>
                <option value="scope_1">Scope 1 – Direct</option>
                <option value="scope_2_location">Scope 2 – Location-based</option>
                <option value="scope_2_market">Scope 2 – Market-based</option>
                <option value="scope_3">Scope 3 – Value Chain</option>
              </select>
            </div>
            <div>
              <label className="label">Source Name *</label>
              <input className="input" placeholder="e.g., Natural gas boiler" value={form.source_name}
                onChange={(e) => setForm((f) => ({ ...f, source_name: e.target.value }))} required />
            </div>
            <div>
              <label className="label">Activity Value *</label>
              <input type="number" step="any" className="input" placeholder="e.g., 10000"
                value={form.activity_value} onChange={(e) => setForm((f) => ({ ...f, activity_value: e.target.value }))} required />
            </div>
            <div>
              <label className="label">Activity Unit *</label>
              <select className="input" value={form.activity_unit} onChange={(e) => setForm((f) => ({ ...f, activity_unit: e.target.value }))}>
                {["kWh", "MWh", "GJ", "m3", "litre", "km", "tonne", "kg"].map((u) => <option key={u}>{u}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Emission Factor *</label>
              <input type="number" step="any" className="input" placeholder="e.g., 0.276"
                value={form.emission_factor_value} onChange={(e) => setForm((f) => ({ ...f, emission_factor_value: e.target.value }))} required />
            </div>
            <div>
              <label className="label">Factor Unit</label>
              <input className="input" placeholder="kgCO2e/kWh"
                value={form.emission_factor_unit} onChange={(e) => setForm((f) => ({ ...f, emission_factor_unit: e.target.value }))} />
            </div>
            <div>
              <label className="label">Source</label>
              <input className="input" placeholder="DEFRA 2023"
                value={form.emission_factor_source} onChange={(e) => setForm((f) => ({ ...f, emission_factor_source: e.target.value }))} />
            </div>
            <div>
              <label className="label">Notes</label>
              <input className="input" placeholder="Optional notes"
                value={form.notes} onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))} />
            </div>
            <div className="md:col-span-2 flex gap-3">
              <button type="button" className="btn-secondary flex-1" onClick={() => setShowForm(false)}>Cancel</button>
              <button type="submit" className="btn-primary flex-1" disabled={createMutation.isPending}>
                {createMutation.isPending ? "Saving..." : "Add Entry"}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Entries table */}
      <div className="card p-0 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <h3 className="font-semibold text-gray-800">Emission Entries ({emissions.length})</h3>
        </div>
        {isLoading ? (
          <div className="p-8 text-center text-gray-400">Loading...</div>
        ) : emissions.length === 0 ? (
          <div className="p-8 text-center">
            <CloudIcon className="h-8 w-8 text-gray-300 mx-auto mb-2" />
            <p className="text-gray-400 text-sm">No emission entries yet. Add your first entry above.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Scope</th>
                  <th>Source</th>
                  <th>Activity</th>
                  <th>EF</th>
                  <th>CO₂e (t)</th>
                  <th></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {emissions.map((e) => (
                  <tr key={e.id}>
                    <td><span className="badge-blue text-xs">{e.scope}</span></td>
                    <td className="font-medium">{e.source_name}</td>
                    <td className="text-gray-500">{e.activity_value?.toLocaleString()} {e.activity_unit}</td>
                    <td className="text-gray-500">{e.emission_factor_value} {e.emission_factor_unit}</td>
                    <td className="font-semibold">{e.co2e_tonnes?.toLocaleString(undefined, { maximumFractionDigits: 3 })}</td>
                    <td>
                      <button onClick={() => deleteMutation.mutate(e.id)} className="text-red-400 hover:text-red-600">
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
