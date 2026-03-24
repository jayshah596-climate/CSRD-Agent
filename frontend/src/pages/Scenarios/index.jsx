import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, LineChart, Line, Legend
} from "recharts";
import { scenarioAPI } from "../../api/client";
import { GlobeAltIcon, ArrowPathIcon } from "@heroicons/react/24/outline";
import toast from "react-hot-toast";

const SCENARIO_COLORS = {
  net_zero_2050: "#2d6a4f",
  below_2c: "#16a34a",
  delayed_transition: "#f59e0b",
  divergent_net_zero: "#0891b2",
  current_policies: "#dc2626",
};

const SECTORS = [
  "default", "oil_gas", "coal", "utilities", "automotive", "aviation",
  "steel", "cement", "chemicals", "real_estate", "financial", "technology",
  "healthcare", "consumer_staples", "agriculture",
];

export default function ScenariosPage() {
  const { projectId } = useParams();
  const [sector, setSector] = useState("default");
  const [totalAssets, setTotalAssets] = useState(100);
  const [results, setResults] = useState(null);

  const { data: ngfsScenarios = [] } = useQuery({
    queryKey: ["ngfs-scenarios", projectId],
    queryFn: () => scenarioAPI.ngfsScenarios(projectId).then((r) => r.data),
  });

  const runMutation = useMutation({
    mutationFn: () => scenarioAPI.run(projectId, { sector, total_assets_eur_m: parseFloat(totalAssets) }),
    onSuccess: (res) => {
      setResults(res.data);
      toast.success("Scenario analysis complete");
    },
    onError: () => toast.error("Scenario analysis failed"),
  });

  // Prepare chart data
  const tempPathwayData = results
    ? ["2030", "2050", "2100"].map((year) => {
        const row = { year };
        Object.entries(results.scenarios || {}).forEach(([key, s]) => {
          row[s.scenario_name] = s.temperature_pathway?.[year];
        });
        return row;
      })
    : [];

  const varChartData = results
    ? Object.entries(results.scenarios || {}).map(([key, s]) => ({
        name: s.scenario_name.replace(" ", "\n"),
        key,
        transition_var: s.value_at_risk?.transition_var_eur_m || 0,
        physical_var: s.value_at_risk?.physical_var_eur_m || 0,
      }))
    : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Climate Scenario Analysis</h1>
          <p className="text-gray-500 text-sm mt-1">NGFS Phase 4 scenarios with temperature pathways and Value at Risk</p>
        </div>
      </div>

      {/* Configuration */}
      <div className="card">
        <h3 className="font-semibold text-gray-800 mb-4">Scenario Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="label">Sector</label>
            <select className="input" value={sector} onChange={(e) => setSector(e.target.value)}>
              {SECTORS.map((s) => <option key={s} value={s}>{s.replace(/_/g, " ")}</option>)}
            </select>
          </div>
          <div>
            <label className="label">Total Assets (EUR Million)</label>
            <input type="number" className="input" value={totalAssets}
              onChange={(e) => setTotalAssets(e.target.value)} min="0" />
          </div>
          <div className="flex items-end">
            <button className="btn-primary w-full" onClick={() => runMutation.mutate()}
              disabled={runMutation.isPending}>
              <ArrowPathIcon className={`h-4 w-4 mr-2 ${runMutation.isPending ? "animate-spin" : ""}`} />
              {runMutation.isPending ? "Running..." : "Run Analysis"}
            </button>
          </div>
        </div>
        <p className="text-xs text-gray-400">
          Analysis based on NGFS Phase 4 (2023) scenarios. Physical and transition risks calculated using
          sector-adjusted multipliers aligned with TCFD recommendations.
        </p>
      </div>

      {/* NGFS Scenarios overview */}
      {ngfsScenarios.length > 0 && !results && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {ngfsScenarios.map((s) => (
            <div key={s.key} className="card">
              <div className="flex items-center justify-between mb-2">
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                  s.category === "orderly" ? "bg-green-100 text-green-700" :
                  s.category === "disorderly" ? "bg-yellow-100 text-yellow-700" :
                  "bg-red-100 text-red-700"
                }`}>
                  {s.category}
                </span>
                <span className="text-xs font-bold" style={{ color: SCENARIO_COLORS[s.key] }}>
                  {s.temperature_2050}°C by 2050
                </span>
              </div>
              <h4 className="font-semibold text-gray-900 text-sm mb-1">{s.name}</h4>
              <p className="text-xs text-gray-500 mb-3">{s.description}</p>
              <div className="flex gap-2">
                <div className="flex-1 text-center">
                  <p className="text-xs text-gray-400">Transition Risk</p>
                  <RiskBadge level={s.transition_risk} />
                </div>
                <div className="flex-1 text-center">
                  <p className="text-xs text-gray-400">Physical Risk</p>
                  <RiskBadge level={s.physical_risk} />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Results */}
      {results && (
        <>
          {/* Temperature pathways chart */}
          <div className="card">
            <h3 className="font-semibold text-gray-800 mb-4">Temperature Pathways (°C above pre-industrial)</h3>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={tempPathwayData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="year" />
                <YAxis domain={[1, 4]} />
                <Tooltip />
                <Legend />
                {Object.entries(results.scenarios).map(([key, s]) => (
                  <Line key={key} type="monotone" dataKey={s.scenario_name}
                    stroke={SCENARIO_COLORS[key]} strokeWidth={2}
                    dot={{ r: 4 }} />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Value at Risk */}
          <div className="card">
            <h3 className="font-semibold text-gray-800 mb-1">Value at Risk by Scenario (EUR Million)</h3>
            <p className="text-xs text-gray-400 mb-4">
              Estimated asset value at risk from transition and physical climate risks
            </p>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={varChartData} barGap={4}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v) => [`EUR ${v.toFixed(1)}M`]} />
                <Legend />
                <Bar dataKey="transition_var" name="Transition VaR" fill="#1e3a5f" radius={[3, 3, 0, 0]} />
                <Bar dataKey="physical_var" name="Physical VaR" fill="#2d6a4f" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Scenario details table */}
          <div className="card p-0 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-100">
              <h3 className="font-semibold text-gray-800">Detailed Scenario Results</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="table">
                <thead>
                  <tr>
                    <th>Scenario</th>
                    <th>Temp 2050</th>
                    <th>Carbon Price 2030</th>
                    <th>Carbon Cost 2030</th>
                    <th>Total VaR</th>
                    <th>VaR %</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {Object.entries(results.scenarios).map(([key, s]) => (
                    <tr key={key}>
                      <td>
                        <div>
                          <p className="font-medium text-sm">{s.scenario_name}</p>
                          <p className="text-xs text-gray-400 capitalize">{s.category}</p>
                        </div>
                      </td>
                      <td className="font-semibold">{s.temperature_pathway?.["2050"]}°C</td>
                      <td>USD {s.carbon_price?.["2030"]}/tCO₂e</td>
                      <td>
                        {s.carbon_cost_impact?.total_exposure_usd
                          ? `USD ${(s.carbon_cost_impact.total_exposure_usd / 1000000).toFixed(1)}M`
                          : "—"}
                      </td>
                      <td className="font-semibold">
                        EUR {s.value_at_risk?.total_var_eur_m?.toFixed(1)}M
                      </td>
                      <td>
                        <span className={`font-medium ${
                          (s.value_at_risk?.total_var_pct || 0) > 20 ? "text-red-600" :
                          (s.value_at_risk?.total_var_pct || 0) > 10 ? "text-yellow-600" : "text-green-600"
                        }`}>
                          {s.value_at_risk?.total_var_pct?.toFixed(1)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function RiskBadge({ level }) {
  const colorMap = {
    low: "bg-green-100 text-green-700",
    low_medium: "bg-lime-100 text-lime-700",
    medium: "bg-yellow-100 text-yellow-700",
    high: "bg-orange-100 text-orange-700",
    very_high: "bg-red-100 text-red-700",
  };
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${colorMap[level] || "bg-gray-100 text-gray-600"}`}>
      {level?.replace("_", " ")}
    </span>
  );
}
