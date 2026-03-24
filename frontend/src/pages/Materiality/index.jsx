import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer } from "recharts";
import { materialityAPI } from "../../api/client";
import toast from "react-hot-toast";
import { CheckIcon } from "@heroicons/react/24/outline";

const ESRS_COLORS = {
  E1: "#1e3a5f", E2: "#2d6a4f", E3: "#0891b2", E4: "#16a34a", E5: "#ca8a04",
  S1: "#7c3aed", S2: "#db2777", S3: "#dc2626", S4: "#ea580c", G1: "#374151",
};

export default function MaterialityAssessment() {
  const { projectId } = useParams();
  const qc = useQueryClient();
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [scores, setScores] = useState({});

  const { data: topics = [], isLoading } = useQuery({
    queryKey: ["materiality-topics", projectId],
    queryFn: () => materialityAPI.topics(projectId).then((r) => r.data),
    onSuccess: (data) => {
      const s = {};
      data.forEach((t) => {
        s[t.id] = {
          impact_scale: t.impact_scale || 3,
          impact_scope: t.impact_scope || 3,
          impact_irremediability: t.impact_irremediability || 3,
          impact_likelihood: t.impact_likelihood || 3,
          financial_magnitude: t.financial_magnitude || 3,
          financial_likelihood: t.financial_likelihood || 3,
        };
      });
      setScores(s);
    },
  });

  const { data: heatmap } = useQuery({
    queryKey: ["materiality-heatmap", projectId],
    queryFn: () => materialityAPI.heatmap(projectId).then((r) => r.data),
  });

  const updateMutation = useMutation({
    mutationFn: ({ topicId, data }) => materialityAPI.updateTopic(projectId, topicId, data),
    onSuccess: () => {
      qc.invalidateQueries(["materiality-topics", projectId]);
      qc.invalidateQueries(["materiality-heatmap", projectId]);
      toast.success("Scores updated");
    },
    onError: () => toast.error("Failed to update"),
  });

  const completeMutation = useMutation({
    mutationFn: () => materialityAPI.complete(projectId),
    onSuccess: (res) => {
      toast.success(`Materiality completed: ${res.data.material_topics} material topics identified`);
      qc.invalidateQueries(["project", projectId]);
    },
  });

  const handleSaveScores = (topic) => {
    const s = scores[topic.id] || {};
    updateMutation.mutate({
      topicId: topic.id,
      data: { topic_id: topic.id, ...s },
    });
  };

  const materialTopics = topics.filter((t) => t.is_material);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Double Materiality Assessment</h1>
          <p className="text-gray-500 text-sm mt-1">
            Score each ESRS topic on impact and financial materiality per EFRAG DMA methodology
          </p>
        </div>
        <button
          className="btn-primary"
          onClick={() => completeMutation.mutate()}
          disabled={completeMutation.isPending}
        >
          <CheckIcon className="h-4 w-4 mr-2" />
          Complete Assessment
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="card text-center">
          <p className="text-3xl font-bold text-gray-900">{topics.length}</p>
          <p className="text-sm text-gray-500 mt-1">Total Topics</p>
        </div>
        <div className="card text-center">
          <p className="text-3xl font-bold text-green-700">{materialTopics.length}</p>
          <p className="text-sm text-gray-500 mt-1">Material Topics</p>
        </div>
        <div className="card text-center">
          <p className="text-3xl font-bold text-blue-700">
            {topics.filter((t) => t.impact_score && t.impact_score > 0).length}
          </p>
          <p className="text-sm text-gray-500 mt-1">Assessed</p>
        </div>
      </div>

      {/* Heatmap */}
      {heatmap?.data_points?.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-gray-800 mb-1">Materiality Matrix</h3>
          <p className="text-xs text-gray-400 mb-4">Topics above the threshold line (40) are considered material</p>
          <ResponsiveContainer width="100%" height={320}>
            <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="x" name="Financial Materiality" type="number" domain={[0, 100]}
                label={{ value: "Financial Materiality", position: "insideBottom", offset: -10, fontSize: 12 }} />
              <YAxis dataKey="y" name="Impact Materiality" type="number" domain={[0, 100]}
                label={{ value: "Impact Materiality", angle: -90, position: "insideLeft", fontSize: 12 }} />
              <Tooltip
                content={({ payload }) => {
                  if (!payload?.length) return null;
                  const d = payload[0]?.payload;
                  return (
                    <div className="bg-white border border-gray-200 rounded-lg p-3 shadow text-xs">
                      <p className="font-semibold">{d?.label}</p>
                      <p className="text-gray-500">{d?.esrs_standard}</p>
                      <p>Impact: {d?.y}</p>
                      <p>Financial: {d?.x}</p>
                      <p className={d?.is_material ? "text-green-600 font-semibold" : "text-gray-400"}>
                        {d?.is_material ? "✓ Material" : "Not Material"}
                      </p>
                    </div>
                  );
                }}
              />
              <ReferenceLine x={40} stroke="#ef4444" strokeDasharray="5 5" strokeWidth={1.5} />
              <ReferenceLine y={40} stroke="#ef4444" strokeDasharray="5 5" strokeWidth={1.5} />
              <Scatter
                data={heatmap.data_points}
                fill="#1e3a5f"
                shape={(props) => {
                  const { cx, cy, payload } = props;
                  const color = ESRS_COLORS[payload.esrs_standard] || "#6b7280";
                  return (
                    <g>
                      <circle cx={cx} cy={cy} r={payload.is_material ? 8 : 5} fill={color} fillOpacity={0.8} />
                    </g>
                  );
                }}
              />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Topics table */}
      <div className="card p-0 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h3 className="font-semibold text-gray-800">ESRS Topics Scoring</h3>
          <span className="text-xs text-gray-400">Score 1 (low) – 5 (high)</span>
        </div>
        {isLoading ? (
          <div className="p-8 text-center text-gray-400">Loading topics...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>ESRS</th>
                  <th>Topic</th>
                  <th>Impact Score</th>
                  <th>Financial Score</th>
                  <th>Material?</th>
                  <th></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {topics.map((topic) => (
                  <React.Fragment key={topic.id}>
                    <tr
                      className="cursor-pointer"
                      onClick={() => setSelectedTopic(selectedTopic?.id === topic.id ? null : topic)}
                    >
                      <td>
                        <span
                          className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold text-white"
                          style={{ backgroundColor: ESRS_COLORS[topic.esrs_standard] }}
                        >
                          {topic.esrs_standard}
                        </span>
                      </td>
                      <td className="font-medium">{topic.esrs_topic}</td>
                      <td>
                        <ScoreBar value={topic.impact_score} />
                      </td>
                      <td>
                        <ScoreBar value={topic.financial_score} color="green" />
                      </td>
                      <td>
                        {topic.is_material ? (
                          <span className="badge-green">Material</span>
                        ) : (
                          <span className="badge-gray">Not material</span>
                        )}
                      </td>
                      <td className="text-blue-500 text-xs">Edit ▸</td>
                    </tr>
                    {selectedTopic?.id === topic.id && (
                      <tr>
                        <td colSpan={6} className="bg-blue-50 px-6 py-4">
                          <ScoreEditor
                            topic={topic}
                            scores={scores[topic.id] || {}}
                            onChange={(k, v) =>
                              setScores((s) => ({ ...s, [topic.id]: { ...(s[topic.id] || {}), [k]: v } }))
                            }
                            onSave={() => handleSaveScores(topic)}
                            saving={updateMutation.isPending}
                          />
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function ScoreBar({ value, color = "blue" }) {
  const pct = ((value || 0) / 100) * 100;
  const colors = { blue: "bg-blue-500", green: "bg-green-500" };
  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
        <div className={`h-full ${colors[color]} rounded-full`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-gray-600">{(value || 0).toFixed(0)}</span>
    </div>
  );
}

function ScoreEditor({ topic, scores, onChange, onSave, saving }) {
  const fields = [
    { key: "impact_scale", label: "Impact Scale (1-5)", group: "Impact" },
    { key: "impact_scope", label: "Impact Scope (1-5)", group: "Impact" },
    { key: "impact_irremediability", label: "Irremediability (1-5)", group: "Impact" },
    { key: "impact_likelihood", label: "Likelihood – Impact (1-5)", group: "Impact" },
    { key: "financial_magnitude", label: "Financial Magnitude (1-5)", group: "Financial" },
    { key: "financial_likelihood", label: "Likelihood – Financial (1-5)", group: "Financial" },
  ];

  return (
    <div>
      <h4 className="font-semibold text-gray-800 mb-3">{topic.esrs_standard} – {topic.esrs_topic}</h4>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
        {fields.map((f) => (
          <div key={f.key}>
            <label className="text-xs font-medium text-gray-600 mb-1 block">{f.label}</label>
            <input
              type="range" min="1" max="5" step="0.5"
              value={scores[f.key] || 3}
              onChange={(e) => onChange(f.key, parseFloat(e.target.value))}
              className="w-full"
            />
            <span className="text-xs text-gray-500">{scores[f.key] || 3}</span>
          </div>
        ))}
      </div>
      <button className="btn-primary text-sm" onClick={onSave} disabled={saving}>
        {saving ? "Saving..." : "Save Scores"}
      </button>
    </div>
  );
}
