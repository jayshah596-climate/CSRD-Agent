import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  DocumentArrowDownIcon, BeakerIcon, CheckCircleIcon,
  ArrowPathIcon, DocumentTextIcon,
} from "@heroicons/react/24/outline";
import { reportsAPI } from "../../api/client";
import toast from "react-hot-toast";

const FORMAT_CONFIG = {
  pdf: { label: "PDF Report", icon: "📄", color: "red", desc: "ESRS-structured PDF with charts" },
  excel: { label: "Excel Workbook", icon: "📊", color: "green", desc: "KPI tables across worksheets" },
  json: { label: "JSON Export", icon: "{}", color: "gray", desc: "Structured machine-readable data" },
  xbrl: { label: "XBRL Filing", icon: "🏷️", color: "blue", desc: "ESRS XBRL taxonomy tagged output" },
};

export default function ReportsPage() {
  const { projectId } = useParams();
  const qc = useQueryClient();
  const [_generating, _setGenerating] = useState(false);
  const [pollingId, setPollingId] = useState(null);

  const { data: reports = [], isLoading, refetch } = useQuery({
    queryKey: ["reports", projectId],
    queryFn: () => reportsAPI.list(projectId).then((r) => r.data),
    refetchInterval: pollingId ? 3000 : false,
  });

  const generateMutation = useMutation({
    mutationFn: () => reportsAPI.generate(projectId, { include_xbrl: true }),
    onSuccess: (res) => {
      setPollingId(res.data.report_id);
      toast.success("Report generation started…");
      setTimeout(() => {
        setPollingId(null);
        qc.invalidateQueries(["reports", projectId]);
      }, 30000);
    },
    onError: () => toast.error("Failed to start report generation"),
  });

  const latestReport = reports[0];
  const isGenerating = latestReport?.status === "generating" || generateMutation.isPending;

  const handleDownload = (reportId, format) => {
    const url = reportsAPI.downloadUrl(projectId, reportId, format);
    window.open(url, "_blank");
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Report Generation</h1>
          <p className="text-gray-500 text-sm mt-1">
            Generate ESRS-compliant reports with AI narratives, XBRL tagging, and multi-format export
          </p>
        </div>
        <button
          className="btn-primary"
          onClick={() => generateMutation.mutate()}
          disabled={isGenerating}
        >
          {isGenerating ? (
            <>
              <ArrowPathIcon className="h-4 w-4 mr-2 animate-spin" />
              Generating…
            </>
          ) : (
            <>
              <BeakerIcon className="h-4 w-4 mr-2" />
              Generate Report
            </>
          )}
        </button>
      </div>

      {/* What will be generated */}
      <div className="card">
        <h3 className="font-semibold text-gray-800 mb-4">Report Contents</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            "General Disclosures (ESRS 2 – GOV, SBM, IRO, MDR)",
            "Climate Change (ESRS E1 – Policy, Strategy, Targets)",
            "GHG Emissions (Scope 1, 2, 3 – ESRS E1-6)",
            "Double Materiality Assessment heatmap",
            "IRO Analysis (Physical & Transition Risks)",
            "NGFS Climate Scenario Analysis",
            "Own Workforce KPIs (ESRS S1)",
            "Governance & Business Conduct (ESRS G1)",
            "AI-generated ESRS-compliant narratives",
            "XBRL digital taxonomy tagging",
          ].map((item) => (
            <div key={item} className="flex items-start gap-2">
              <CheckCircleIcon className="h-4 w-4 text-green-500 shrink-0 mt-0.5" />
              <span className="text-sm text-gray-700">{item}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Export formats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Object.entries(FORMAT_CONFIG).map(([fmt, config]) => (
          <div key={fmt} className="card text-center">
            <div className="text-2xl mb-2">{config.icon}</div>
            <p className="font-semibold text-gray-800 text-sm">{config.label}</p>
            <p className="text-xs text-gray-400 mt-1">{config.desc}</p>
          </div>
        ))}
      </div>

      {/* Generation status */}
      {isGenerating && (
        <div className="card border-blue-200 border-2 bg-blue-50">
          <div className="flex items-center gap-3">
            <ArrowPathIcon className="h-6 w-6 text-blue-600 animate-spin" />
            <div>
              <p className="font-semibold text-blue-800">Generating your CSRD report…</p>
              <p className="text-sm text-blue-600">
                AI is writing ESRS-compliant narratives and generating all export formats. This may take 20–60 seconds.
              </p>
            </div>
          </div>
          <div className="mt-3 h-1.5 bg-blue-200 rounded-full overflow-hidden">
            <div className="h-full bg-blue-600 rounded-full animate-pulse w-3/4" />
          </div>
        </div>
      )}

      {/* Reports list */}
      {isLoading ? (
        <div className="text-center py-8 text-gray-400">Loading reports…</div>
      ) : reports.length === 0 ? (
        <div className="card py-12 text-center">
          <DocumentTextIcon className="h-10 w-10 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">No reports generated yet</p>
          <p className="text-gray-400 text-sm mt-1">
            Complete data collection, materiality, and emissions steps, then click "Generate Report"
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          <h3 className="font-semibold text-gray-800">Generated Reports ({reports.length})</h3>
          {reports.map((report) => (
            <ReportCard
              key={report.id}
              report={report}
              onDownload={handleDownload}
              onRefresh={() => refetch()}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ReportCard({ report, onDownload, onRefresh }) {
  const statusMap = {
    generating: { label: "Generating", class: "badge-blue", animate: true },
    draft: { label: "Draft", class: "badge-gray", animate: false },
    final: { label: "Final", class: "badge-green", animate: false },
    published: { label: "Published", class: "badge-green", animate: false },
    failed: { label: "Failed", class: "badge-red", animate: false },
  };
  const s = statusMap[report.status] || statusMap.draft;

  const formats = [
    { key: "pdf", label: "PDF", available: report.pdf_available },
    { key: "excel", label: "Excel", available: report.excel_available },
    { key: "json", label: "JSON", available: report.json_available },
    { key: "xbrl", label: "XBRL", available: report.xbrl_available },
  ];

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h4 className="font-semibold text-gray-900">{report.title}</h4>
          <p className="text-xs text-gray-400 mt-0.5">
            FY {report.reporting_year} · Version {report.version} · Generated{" "}
            {report.created_at ? new Date(report.created_at).toLocaleDateString() : "—"}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {s.animate && (
            <ArrowPathIcon className="h-4 w-4 text-blue-500 animate-spin" />
          )}
          <span className={s.class}>{s.label}</span>
        </div>
      </div>

      {report.status === "generating" ? (
        <div className="flex items-center gap-2 py-2">
          <div className="h-1.5 flex-1 bg-blue-100 rounded-full overflow-hidden">
            <div className="h-full w-1/2 bg-blue-500 rounded-full animate-pulse" />
          </div>
          <button onClick={onRefresh} className="text-xs text-blue-600 hover:underline">Refresh</button>
        </div>
      ) : (
        <div className="flex flex-wrap gap-2 mt-3">
          {formats.map(({ key, label, available }) => (
            <button
              key={key}
              onClick={() => available && onDownload(report.id, key)}
              disabled={!available}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                available
                  ? "bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200"
                  : "bg-gray-50 text-gray-300 border border-gray-100 cursor-not-allowed"
              }`}
            >
              <DocumentArrowDownIcon className="h-3.5 w-3.5" />
              {label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
