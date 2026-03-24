import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { PlusIcon, CheckBadgeIcon, DocumentTextIcon } from "@heroicons/react/24/outline";
import { dataAPI } from "../../api/client";
import toast from "react-hot-toast";

const ESRS_SECTIONS = [
  { id: "E1", label: "E1 – Climate Change", color: "blue" },
  { id: "E2", label: "E2 – Pollution", color: "green" },
  { id: "E3", label: "E3 – Water", color: "cyan" },
  { id: "E4", label: "E4 – Biodiversity", color: "emerald" },
  { id: "E5", label: "E5 – Circular Economy", color: "yellow" },
  { id: "S1", label: "S1 – Own Workforce", color: "purple" },
  { id: "S2", label: "S2 – Value Chain", color: "pink" },
  { id: "S3", label: "S3 – Communities", color: "rose" },
  { id: "S4", label: "S4 – Consumers", color: "orange" },
  { id: "G1", label: "G1 – Governance", color: "gray" },
];

// Suggested ESRS datapoints for quick-entry
const SUGGESTED_DATAPOINTS = {
  E1: [
    { datapoint_name: "Gross Scope 1 GHG Emissions", data_type: "numeric", unit: "tCO2e", datapoint_id: "E1-6_scope1_emissions" },
    { datapoint_name: "Gross Scope 2 GHG Emissions (location-based)", data_type: "numeric", unit: "tCO2e", datapoint_id: "E1-6_scope2_location" },
    { datapoint_name: "Total Energy Consumption", data_type: "numeric", unit: "MWh", datapoint_id: "E1-5_total_energy" },
    { datapoint_name: "Renewable Energy Share", data_type: "numeric", unit: "%", datapoint_id: "E1-5_renewable_pct" },
    { datapoint_name: "GHG Reduction Target", data_type: "text", unit: null, datapoint_id: "E1-4_ghg_target" },
    { datapoint_name: "Net Zero Target Year", data_type: "numeric", unit: "year", datapoint_id: "E1-4_net_zero_year" },
  ],
  S1: [
    { datapoint_name: "Total Employees", data_type: "numeric", unit: "headcount", datapoint_id: "S1-6_employee_total" },
    { datapoint_name: "Female Employees (%)", data_type: "numeric", unit: "%", datapoint_id: "S1-9_female_pct" },
    { datapoint_name: "Lost Time Injury Rate (LTIR)", data_type: "numeric", unit: "per M hours", datapoint_id: "S1-14_ltir" },
    { datapoint_name: "Gender Pay Gap (unadjusted)", data_type: "numeric", unit: "%", datapoint_id: "S1-16_gender_pay_gap" },
    { datapoint_name: "Training Hours per FTE", data_type: "numeric", unit: "hours", datapoint_id: "S1-13_training_hours" },
    { datapoint_name: "Fatalities", data_type: "numeric", unit: "count", datapoint_id: "S1-14_fatalities" },
  ],
  G1: [
    { datapoint_name: "Confirmed Corruption Incidents", data_type: "numeric", unit: "count", datapoint_id: "G1-4_corruption_incidents" },
    { datapoint_name: "% Employees Trained on Anti-Corruption", data_type: "numeric", unit: "%", datapoint_id: "G1-3_anti_corruption_training" },
    { datapoint_name: "Average Payment Period to SMEs", data_type: "numeric", unit: "days", datapoint_id: "G1-6_avg_payment_days" },
    { datapoint_name: "Anti-corruption Policy in Place", data_type: "boolean", unit: null, datapoint_id: "G1-1_anti_corruption_policy" },
  ],
};

export default function DataCollection() {
  const { projectId } = useParams();
  const qc = useQueryClient();
  const [selectedStandard, setSelectedStandard] = useState("E1");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    esrs_standard: "E1",
    esrs_disclosure: "",
    datapoint_id: "",
    datapoint_name: "",
    data_type: "numeric",
    value_numeric: "",
    value_text: "",
    value_boolean: false,
    unit: "",
    source_type: "manual",
    is_estimated: false,
    notes: "",
  });

  const { data: entries = [], isLoading } = useQuery({
    queryKey: ["data-entries", projectId, selectedStandard],
    queryFn: () => dataAPI.list(projectId, selectedStandard).then((r) => r.data),
  });

  const { data: validation } = useQuery({
    queryKey: ["data-validate", projectId],
    queryFn: () => dataAPI.validate?.(projectId)?.then((r) => r.data) ?? null,
    enabled: false,
  });

  const createMutation = useMutation({
    mutationFn: (data) => dataAPI.create(projectId, data),
    onSuccess: () => {
      qc.invalidateQueries(["data-entries", projectId]);
      setShowForm(false);
      toast.success("Data point saved");
    },
    onError: () => toast.error("Failed to save data point"),
  });

  const handleSuggestedEntry = (dp) => {
    setForm({
      ...form,
      esrs_standard: selectedStandard,
      datapoint_id: dp.datapoint_id,
      datapoint_name: dp.datapoint_name,
      data_type: dp.data_type,
      unit: dp.unit || "",
    });
    setShowForm(true);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {
      esrs_standard: selectedStandard,
      esrs_disclosure: form.esrs_disclosure,
      datapoint_id: form.datapoint_id,
      datapoint_name: form.datapoint_name,
      data_type: form.data_type,
      unit: form.unit,
      source_type: form.source_type,
      is_estimated: form.is_estimated,
      notes: form.notes,
    };
    if (form.data_type === "numeric") payload.value_numeric = parseFloat(form.value_numeric);
    else if (form.data_type === "boolean") payload.value_boolean = form.value_boolean;
    else payload.value_text = form.value_text;
    createMutation.mutate(payload);
  };

  const suggestedDps = SUGGESTED_DATAPOINTS[selectedStandard] || [];
  const enteredIds = new Set(entries.map((e) => e.datapoint_id).filter(Boolean));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Data Collection</h1>
          <p className="text-gray-500 text-sm mt-1">
            Enter ESRS-required data points for each standard
          </p>
        </div>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          <PlusIcon className="h-4 w-4 mr-2" />
          Add Data Point
        </button>
      </div>

      {/* Standard selector */}
      <div className="flex flex-wrap gap-2">
        {ESRS_SECTIONS.map((s) => (
          <button
            key={s.id}
            onClick={() => setSelectedStandard(s.id)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              selectedStandard === s.id
                ? "bg-blue-900 text-white"
                : "bg-white border border-gray-200 text-gray-600 hover:border-blue-300"
            }`}
          >
            {s.id}
          </button>
        ))}
      </div>

      {/* Suggested data points */}
      {suggestedDps.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-gray-800 mb-3">
            Suggested Datapoints for {selectedStandard}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {suggestedDps.map((dp) => {
              const entered = enteredIds.has(dp.datapoint_id);
              return (
                <button
                  key={dp.datapoint_id}
                  onClick={() => !entered && handleSuggestedEntry(dp)}
                  disabled={entered}
                  className={`flex items-center justify-between p-3 rounded-lg border text-left transition-colors ${
                    entered
                      ? "border-green-200 bg-green-50 cursor-default"
                      : "border-gray-200 hover:border-blue-300 hover:bg-blue-50"
                  }`}
                >
                  <div>
                    <p className="text-sm font-medium text-gray-800">{dp.datapoint_name}</p>
                    <p className="text-xs text-gray-400">{dp.data_type}{dp.unit ? ` · ${dp.unit}` : ""}</p>
                  </div>
                  {entered ? (
                    <CheckBadgeIcon className="h-5 w-5 text-green-500 shrink-0" />
                  ) : (
                    <PlusIcon className="h-4 w-4 text-gray-300 shrink-0" />
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Add form */}
      {showForm && (
        <div className="card border-2 border-blue-200">
          <h3 className="font-semibold text-gray-800 mb-4">Add Data Point – {selectedStandard}</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="label">Datapoint Name *</label>
              <input className="input" placeholder="e.g., Total GHG Emissions"
                value={form.datapoint_name}
                onChange={(e) => setForm((f) => ({ ...f, datapoint_name: e.target.value }))} required />
            </div>
            <div>
              <label className="label">Data Type</label>
              <select className="input" value={form.data_type}
                onChange={(e) => setForm((f) => ({ ...f, data_type: e.target.value }))}>
                <option value="numeric">Numeric</option>
                <option value="text">Text / Narrative</option>
                <option value="boolean">Yes / No</option>
              </select>
            </div>
            <div>
              <label className="label">Unit</label>
              <input className="input" placeholder="e.g., tCO2e, %, MWh"
                value={form.unit}
                onChange={(e) => setForm((f) => ({ ...f, unit: e.target.value }))} />
            </div>
            {form.data_type === "numeric" && (
              <div>
                <label className="label">Value *</label>
                <input type="number" step="any" className="input" placeholder="0.00"
                  value={form.value_numeric}
                  onChange={(e) => setForm((f) => ({ ...f, value_numeric: e.target.value }))} required />
              </div>
            )}
            {form.data_type === "text" && (
              <div className="md:col-span-2">
                <label className="label">Value *</label>
                <textarea className="input" rows={3} placeholder="Enter narrative text..."
                  value={form.value_text}
                  onChange={(e) => setForm((f) => ({ ...f, value_text: e.target.value }))} required />
              </div>
            )}
            {form.data_type === "boolean" && (
              <div>
                <label className="label">Value</label>
                <select className="input" value={form.value_boolean ? "true" : "false"}
                  onChange={(e) => setForm((f) => ({ ...f, value_boolean: e.target.value === "true" }))}>
                  <option value="true">Yes</option>
                  <option value="false">No</option>
                </select>
              </div>
            )}
            <div>
              <label className="label">ESRS Disclosure</label>
              <input className="input" placeholder="e.g., E1-6"
                value={form.esrs_disclosure}
                onChange={(e) => setForm((f) => ({ ...f, esrs_disclosure: e.target.value }))} />
            </div>
            <div>
              <label className="label">Source</label>
              <select className="input" value={form.source_type}
                onChange={(e) => setForm((f) => ({ ...f, source_type: e.target.value }))}>
                <option value="manual">Manual Entry</option>
                <option value="file_upload">File Upload</option>
                <option value="api">API / System</option>
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="label">Notes</label>
              <input className="input" placeholder="Optional notes or data source reference"
                value={form.notes}
                onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))} />
            </div>
            <div className="flex items-center gap-2">
              <input type="checkbox" id="estimated" className="h-4 w-4 rounded"
                checked={form.is_estimated}
                onChange={(e) => setForm((f) => ({ ...f, is_estimated: e.target.checked }))} />
              <label htmlFor="estimated" className="text-sm text-gray-600">Mark as estimated value</label>
            </div>
            <div className="md:col-span-2 flex gap-3">
              <button type="button" className="btn-secondary flex-1"
                onClick={() => setShowForm(false)}>Cancel</button>
              <button type="submit" className="btn-primary flex-1" disabled={createMutation.isPending}>
                {createMutation.isPending ? "Saving…" : "Save Datapoint"}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Entries table */}
      <div className="card p-0 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h3 className="font-semibold text-gray-800">
            {selectedStandard} Data Points ({entries.length})
          </h3>
          <span className="text-xs text-gray-400">
            {entries.filter((e) => e.is_validated).length} validated
          </span>
        </div>
        {isLoading ? (
          <div className="p-8 text-center text-gray-400">Loading…</div>
        ) : entries.length === 0 ? (
          <div className="p-8 text-center">
            <DocumentTextIcon className="h-8 w-8 text-gray-300 mx-auto mb-2" />
            <p className="text-gray-400 text-sm">No data points for {selectedStandard} yet.</p>
            <p className="text-gray-300 text-xs mt-1">Use the suggested datapoints above or add manually.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Datapoint</th>
                  <th>Value</th>
                  <th>Unit</th>
                  <th>Source</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {entries.map((e) => (
                  <tr key={e.id}>
                    <td>
                      <div>
                        <p className="font-medium text-sm">{e.datapoint_name}</p>
                        {e.esrs_disclosure && (
                          <p className="text-xs text-gray-400">{e.esrs_disclosure}</p>
                        )}
                      </div>
                    </td>
                    <td className="font-mono text-sm">
                      {e.value_numeric != null
                        ? e.value_numeric.toLocaleString()
                        : e.value_boolean != null
                        ? e.value_boolean ? "Yes" : "No"
                        : <span className="text-gray-400 line-clamp-1 max-w-xs">{e.value_text}</span>}
                    </td>
                    <td className="text-gray-500 text-xs">{e.unit || "—"}</td>
                    <td>
                      <span className="badge-gray capitalize">{e.source_type?.replace("_", " ")}</span>
                    </td>
                    <td>
                      {e.is_estimated ? (
                        <span className="badge-yellow">Estimated</span>
                      ) : e.is_validated ? (
                        <span className="badge-green">Validated</span>
                      ) : (
                        <span className="badge-gray">Entered</span>
                      )}
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
