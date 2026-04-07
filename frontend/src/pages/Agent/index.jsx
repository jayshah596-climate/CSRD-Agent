import React, { useState, useRef, useCallback } from "react";
import {
  SparklesIcon,
  PlayIcon,
  StopIcon,
  DocumentArrowDownIcon,
  ClipboardDocumentIcon,
  CheckCircleIcon,
  ClockIcon,
  ArrowPathIcon,
} from "@heroicons/react/24/outline";

// ─── Step definitions ────────────────────────────────────────────────────────

const STEPS = [
  { id: "wave_eligibility",    label: "Wave Eligibility",   tag: "scratchpad",                    desc: "CSRD reporting wave determination" },
  { id: "esrs_modules",        label: "ESRS Modules",        tag: "esrs_modules",                  desc: "Applicable standards & metrics" },
  { id: "data_processing",     label: "Data Processing",     tag: "data_processing",               desc: "Calculations & data quality" },
  { id: "double_materiality",  label: "Double Materiality",  tag: "double_materiality_assessment", desc: "Impact & financial materiality" },
  { id: "iro_analysis",        label: "IRO Analysis",        tag: "iro_analysis",                  desc: "Impacts, Risks & Opportunities" },
  { id: "climate_scenario",    label: "Climate Scenarios",   tag: "climate_scenario_analysis",     desc: "1.5°C / 2°C / 3°C+ scenarios" },
  { id: "esg_report",          label: "ESG Report",          tag: "esg_report",                    desc: "Full CSRD-compliant report" },
  { id: "xbrl_specifications", label: "XBRL Specs",          tag: "xbrl_specifications",           desc: "Digital reporting specifications" },
];

const ESRS_MODULES = [
  { id: "E1", label: "E1 — Climate Change",           category: "Environmental" },
  { id: "E2", label: "E2 — Pollution",                category: "Environmental" },
  { id: "E3", label: "E3 — Water & Marine Resources", category: "Environmental" },
  { id: "E4", label: "E4 — Biodiversity & Ecosystems",category: "Environmental" },
  { id: "E5", label: "E5 — Circular Economy",         category: "Environmental" },
  { id: "S1", label: "S1 — Own Workforce",            category: "Social" },
  { id: "S2", label: "S2 — Value Chain Workers",      category: "Social" },
  { id: "S3", label: "S3 — Affected Communities",     category: "Social" },
  { id: "S4", label: "S4 — Consumers & End-users",    category: "Social" },
  { id: "G1", label: "G1 — Business Conduct",         category: "Governance" },
];

const COMPANY_TYPES = ["Large EU", "Large EU (listed)", "SME (listed)", "Non-EU"];

const API_BASE = process.env.REACT_APP_API_URL || "/api";

// ─── Helpers ─────────────────────────────────────────────────────────────────

function parseSSEChunk(chunk) {
  return chunk
    .split("\n")
    .filter((line) => line.startsWith("data: "))
    .map((line) => line.slice(6))
    .join("");
}

function unescapeNewlines(text) {
  return text.replace(/\\n/g, "\n");
}

function detectCurrentStep(text) {
  let current = null;
  for (const step of STEPS) {
    const openTag = `<${step.tag}>`;
    const closeTag = `</${step.tag}>`;
    if (text.includes(openTag)) {
      if (!text.includes(closeTag)) {
        current = step.id;
      }
    }
  }
  return current;
}

function extractSections(text) {
  const sections = {};
  for (const step of STEPS) {
    const regex = new RegExp(`<${step.tag}>([\\s\\S]*?)<\\/${step.tag}>`, "i");
    const match = text.match(regex);
    sections[step.id] = match ? match[1].trim() : null;
  }
  return sections;
}

function downloadText(filename, content) {
  const blob = new Blob([content], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// ─── Sub-components ──────────────────────────────────────────────────────────

function StepIndicator({ steps, currentStepId, sections, streaming }) {
  return (
    <div className="space-y-1">
      {steps.map((step, idx) => {
        const done = sections[step.id] !== null && sections[step.id] !== undefined && sections[step.id] !== "";
        const active = currentStepId === step.id;
        return (
          <div
            key={step.id}
            className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
              done
                ? "bg-green-50 text-green-800"
                : active
                ? "bg-blue-50 text-blue-800"
                : "text-gray-500"
            }`}
          >
            <span className="flex-shrink-0 w-5 h-5">
              {done ? (
                <CheckCircleIcon className="w-5 h-5 text-green-600" />
              ) : active ? (
                <ArrowPathIcon className="w-5 h-5 text-blue-600 animate-spin" />
              ) : (
                <ClockIcon className="w-5 h-5 text-gray-300" />
              )}
            </span>
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">{step.label}</p>
              <p className="text-xs opacity-70 truncate">{step.desc}</p>
            </div>
            <span className="text-xs font-mono opacity-50">{idx + 1}/8</span>
          </div>
        );
      })}
    </div>
  );
}

function SectionContent({ content, stepLabel }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const handleDownload = () => {
    downloadText(`${stepLabel.replace(/\s+/g, "_")}.txt`, content);
  };

  return (
    <div>
      <div className="flex gap-2 mb-3">
        <button
          onClick={handleCopy}
          className="btn-secondary flex items-center gap-1.5 text-xs py-1 px-2"
        >
          <ClipboardDocumentIcon className="h-3.5 w-3.5" />
          {copied ? "Copied!" : "Copy"}
        </button>
        <button
          onClick={handleDownload}
          className="btn-secondary flex items-center gap-1.5 text-xs py-1 px-2"
        >
          <DocumentArrowDownIcon className="h-3.5 w-3.5" />
          Download
        </button>
      </div>
      <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-800 leading-relaxed whitespace-pre-wrap font-mono overflow-auto max-h-[60vh] border border-gray-200">
        {content || <span className="text-gray-400 italic">No content for this section.</span>}
      </div>
    </div>
  );
}

// ─── Main component ──────────────────────────────────────────────────────────

export default function AgentPage() {
  // ── Form state ──
  const [companyData, setCompanyData] = useState({
    name: "",
    employees: "",
    revenue_eur_m: "",
    country: "",
    fiscal_year: new Date().getFullYear(),
    company_type: "Large EU",
    subject_to_nfrd: false,
    sector: "",
    nace_code: "",
  });
  const [selectedModules, setSelectedModules] = useState(["E1", "S1", "G1"]);
  const [rawData, setRawData] = useState("");

  // ── Streaming state ──
  const [streaming, setStreaming] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState(null);
  const [rawOutput, setRawOutput] = useState("");
  const [currentStepId, setCurrentStepId] = useState(null);
  const [sections, setSections] = useState({});
  const [activeTab, setActiveTab] = useState(null);

  const abortRef = useRef(null);
  const outputRef = useRef("");

  // ── Form handlers ──
  const handleCompanyChange = (field, value) => {
    setCompanyData((prev) => ({ ...prev, [field]: value }));
  };

  const toggleModule = (id) => {
    setSelectedModules((prev) =>
      prev.includes(id) ? prev.filter((m) => m !== id) : [...prev, id]
    );
  };

  const toggleAllModules = () => {
    if (selectedModules.length === ESRS_MODULES.length) {
      setSelectedModules([]);
    } else {
      setSelectedModules(ESRS_MODULES.map((m) => m.id));
    }
  };

  // ── Run analysis ──
  const runAnalysis = useCallback(async () => {
    setStreaming(true);
    setDone(false);
    setError(null);
    setRawOutput("");
    setSections({});
    setCurrentStepId(null);
    setActiveTab(null);
    outputRef.current = "";

    const payload = {
      company_data: {
        ...companyData,
        employees: companyData.employees ? parseInt(companyData.employees) : null,
        revenue_eur_m: companyData.revenue_eur_m ? parseFloat(companyData.revenue_eur_m) : null,
        fiscal_year: parseInt(companyData.fiscal_year),
      },
      reporting_requirements: selectedModules,
      raw_data: rawData,
    };

    try {
      const controller = new AbortController();
      abortRef.current = controller;

      const response = await fetch(`${API_BASE}/agent/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status} ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done: streamDone, value } = await reader.read();
        if (streamDone) break;

        const chunk = decoder.decode(value, { stream: true });
        const text = unescapeNewlines(parseSSEChunk(chunk));

        if (text.startsWith("[ERROR]")) {
          setError(text.replace("[ERROR] ", ""));
          break;
        }
        if (text === "[DONE]") {
          const finalSections = extractSections(outputRef.current);
          setSections(finalSections);
          const firstDone = STEPS.find((s) => finalSections[s.id]);
          if (firstDone) setActiveTab(firstDone.id);
          setDone(true);
          break;
        }

        outputRef.current += text;
        setRawOutput(outputRef.current);

        const step = detectCurrentStep(outputRef.current);
        if (step) setCurrentStepId(step);
      }
    } catch (err) {
      if (err.name !== "AbortError") {
        setError(err.message || "Analysis failed. Please try again.");
      }
    } finally {
      setStreaming(false);
      abortRef.current = null;
    }
  }, [companyData, selectedModules, rawData]);

  const stopAnalysis = () => {
    if (abortRef.current) {
      abortRef.current.abort();
    }
    setStreaming(false);
  };

  const reset = () => {
    setStreaming(false);
    setDone(false);
    setError(null);
    setRawOutput("");
    setSections({});
    setCurrentStepId(null);
    setActiveTab(null);
    outputRef.current = "";
  };

  const downloadFullReport = () => {
    const lines = STEPS.map((step) => {
      const content = sections[step.id];
      if (!content) return "";
      return `${"=".repeat(60)}\n${step.label.toUpperCase()}\n${"=".repeat(60)}\n\n${content}\n\n`;
    }).filter(Boolean);
    downloadText(
      `CSRD_Report_${companyData.name || "Company"}_${companyData.fiscal_year}.txt`,
      lines.join("\n")
    );
  };

  // ── Grouped modules ──
  const envModules = ESRS_MODULES.filter((m) => m.category === "Environmental");
  const socModules = ESRS_MODULES.filter((m) => m.category === "Social");
  const govModules = ESRS_MODULES.filter((m) => m.category === "Governance");

  const completedCount = STEPS.filter((s) => sections[s.id]).length;
  const progress = done ? 100 : streaming ? Math.min(95, Math.round((completedCount / 8) * 100)) : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <SparklesIcon className="h-7 w-7 text-blue-900" />
            CSRD Reporting Agent
          </h1>
          <p className="text-gray-500 mt-1 text-sm">
            AI-powered end-to-end CSRD/ESRS reporting — 8-step analysis powered by Claude
          </p>
        </div>
        {(done || streaming) && (
          <div className="flex gap-2">
            {done && (
              <button onClick={downloadFullReport} className="btn-primary flex items-center gap-2">
                <DocumentArrowDownIcon className="h-4 w-4" />
                Download Full Report
              </button>
            )}
            <button onClick={reset} className="btn-secondary flex items-center gap-2">
              <ArrowPathIcon className="h-4 w-4" />
              New Analysis
            </button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* ── Left panel: Input form ── */}
        <div className="xl:col-span-1 space-y-4">
          {/* Company Information */}
          <div className="card">
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">
              1. Company Information
            </h2>
            <div className="space-y-3">
              <div>
                <label className="label">Company Name *</label>
                <input
                  className="input"
                  placeholder="e.g. Acme GmbH"
                  value={companyData.name}
                  onChange={(e) => handleCompanyChange("name", e.target.value)}
                  disabled={streaming}
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="label">Employees</label>
                  <input
                    type="number"
                    className="input"
                    placeholder="e.g. 500"
                    value={companyData.employees}
                    onChange={(e) => handleCompanyChange("employees", e.target.value)}
                    disabled={streaming}
                  />
                </div>
                <div>
                  <label className="label">Revenue (EUR M)</label>
                  <input
                    type="number"
                    className="input"
                    placeholder="e.g. 120"
                    value={companyData.revenue_eur_m}
                    onChange={(e) => handleCompanyChange("revenue_eur_m", e.target.value)}
                    disabled={streaming}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="label">Country</label>
                  <input
                    className="input"
                    placeholder="e.g. Germany"
                    value={companyData.country}
                    onChange={(e) => handleCompanyChange("country", e.target.value)}
                    disabled={streaming}
                  />
                </div>
                <div>
                  <label className="label">Fiscal Year</label>
                  <input
                    type="number"
                    className="input"
                    placeholder="e.g. 2024"
                    value={companyData.fiscal_year}
                    onChange={(e) => handleCompanyChange("fiscal_year", e.target.value)}
                    disabled={streaming}
                  />
                </div>
              </div>
              <div>
                <label className="label">Company Type</label>
                <select
                  className="input"
                  value={companyData.company_type}
                  onChange={(e) => handleCompanyChange("company_type", e.target.value)}
                  disabled={streaming}
                >
                  {COMPANY_TYPES.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="label">Sector</label>
                  <input
                    className="input"
                    placeholder="e.g. Manufacturing"
                    value={companyData.sector}
                    onChange={(e) => handleCompanyChange("sector", e.target.value)}
                    disabled={streaming}
                  />
                </div>
                <div>
                  <label className="label">NACE Code</label>
                  <input
                    className="input"
                    placeholder="e.g. C25"
                    value={companyData.nace_code}
                    onChange={(e) => handleCompanyChange("nace_code", e.target.value)}
                    disabled={streaming}
                  />
                </div>
              </div>
              <div className="flex items-center gap-2 pt-1">
                <input
                  id="nfrd"
                  type="checkbox"
                  className="h-4 w-4 rounded border-gray-300 text-blue-900 focus:ring-blue-900"
                  checked={companyData.subject_to_nfrd}
                  onChange={(e) => handleCompanyChange("subject_to_nfrd", e.target.checked)}
                  disabled={streaming}
                />
                <label htmlFor="nfrd" className="text-sm text-gray-700 select-none cursor-pointer">
                  Previously subject to NFRD (Wave 1 indicator)
                </label>
              </div>
            </div>
          </div>

          {/* Reporting Requirements */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
                2. Reporting Requirements
              </h2>
              <button
                onClick={toggleAllModules}
                className="text-xs text-blue-700 hover:underline"
                disabled={streaming}
              >
                {selectedModules.length === ESRS_MODULES.length ? "Deselect All" : "Select All"}
              </button>
            </div>
            <p className="text-xs text-gray-500 mb-3">
              ESRS 1 & ESRS 2 (General) are always mandatory. Select topic-specific standards:
            </p>
            {[
              { label: "Environmental", modules: envModules },
              { label: "Social", modules: socModules },
              { label: "Governance", modules: govModules },
            ].map(({ label, modules }) => (
              <div key={label} className="mb-3">
                <p className="text-xs font-semibold text-gray-400 uppercase mb-1">{label}</p>
                <div className="space-y-1">
                  {modules.map((mod) => (
                    <label
                      key={mod.id}
                      className={`flex items-center gap-2 px-2 py-1.5 rounded-md cursor-pointer transition-colors text-sm ${
                        selectedModules.includes(mod.id)
                          ? "bg-blue-50 text-blue-900"
                          : "text-gray-600 hover:bg-gray-50"
                      } ${streaming ? "opacity-60 cursor-not-allowed" : ""}`}
                    >
                      <input
                        type="checkbox"
                        className="h-3.5 w-3.5 rounded border-gray-300 text-blue-900 focus:ring-blue-900"
                        checked={selectedModules.includes(mod.id)}
                        onChange={() => toggleModule(mod.id)}
                        disabled={streaming}
                      />
                      {mod.label}
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Raw Data */}
          <div className="card">
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">
              3. Raw Sustainability Data
            </h2>
            <p className="text-xs text-gray-500 mb-2">
              Paste your metrics, emissions data, workforce statistics, or any other relevant data:
            </p>
            <textarea
              className="input w-full"
              rows={6}
              placeholder={
                "e.g.\nScope 1 emissions: 1,200 tCO2e\nScope 2 (location-based): 800 tCO2e\nScope 2 (market-based): 650 tCO2e\nTotal employees: 523 (52% female)\nGender pay gap: 8.3%\nLTIR: 1.2 per million hours\nRenewable energy: 45%\nWater consumption: 12,000 m³\nAnti-corruption training: 92%"
              }
              value={rawData}
              onChange={(e) => setRawData(e.target.value)}
              disabled={streaming}
            />
          </div>

          {/* Run button */}
          <div>
            {!streaming ? (
              <button
                onClick={runAnalysis}
                disabled={!companyData.name || selectedModules.length === 0}
                className="btn-primary w-full flex items-center justify-center gap-2 py-3 text-base disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <PlayIcon className="h-5 w-5" />
                Run CSRD Analysis
              </button>
            ) : (
              <button
                onClick={stopAnalysis}
                className="w-full flex items-center justify-center gap-2 py-3 text-base rounded-lg bg-red-600 hover:bg-red-700 text-white font-medium transition-colors"
              >
                <StopIcon className="h-5 w-5" />
                Stop Analysis
              </button>
            )}
            {!companyData.name && (
              <p className="text-xs text-gray-400 text-center mt-1">
                Enter a company name to begin
              </p>
            )}
          </div>
        </div>

        {/* ── Right panel: Results ── */}
        <div className="xl:col-span-2 space-y-4">
          {/* Progress & steps */}
          {(streaming || done || error) && (
            <div className="card">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold text-gray-700">
                  {done ? "Analysis Complete" : streaming ? "Analysis Running…" : "Analysis Stopped"}
                </h2>
                <span className="text-sm font-mono text-gray-500">
                  {completedCount}/8 steps
                </span>
              </div>

              {/* Progress bar */}
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden mb-4">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    done ? "bg-green-500" : "bg-blue-600"
                  }`}
                  style={{ width: `${progress}%` }}
                />
              </div>

              <StepIndicator
                steps={STEPS}
                currentStepId={currentStepId}
                sections={sections}
                streaming={streaming}
              />
            </div>
          )}

          {/* Error state */}
          {error && (
            <div className="card border border-red-200 bg-red-50">
              <p className="text-red-700 text-sm font-medium">Analysis Error</p>
              <p className="text-red-600 text-sm mt-1">{error}</p>
              <p className="text-red-500 text-xs mt-2">
                Ensure your ANTHROPIC_API_KEY is configured in the backend environment variables.
              </p>
            </div>
          )}

          {/* Live stream while waiting for sections */}
          {streaming && completedCount === 0 && rawOutput && (
            <div className="card">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Live Output</h3>
              <div className="bg-gray-900 text-green-400 rounded-lg p-4 text-xs font-mono leading-relaxed max-h-64 overflow-auto">
                {rawOutput.slice(-2000)}
                <span className="animate-pulse">▊</span>
              </div>
            </div>
          )}

          {/* Results tabs */}
          {done && completedCount > 0 && (
            <div className="card">
              {/* Tab bar */}
              <div className="flex flex-wrap gap-1 mb-4 border-b border-gray-200 pb-3">
                {STEPS.map((step) => {
                  const hasContent = !!sections[step.id];
                  return (
                    <button
                      key={step.id}
                      onClick={() => hasContent && setActiveTab(step.id)}
                      className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                        activeTab === step.id
                          ? "bg-blue-900 text-white"
                          : hasContent
                          ? "text-gray-600 hover:bg-gray-100"
                          : "text-gray-300 cursor-not-allowed"
                      }`}
                      disabled={!hasContent}
                      title={hasContent ? step.desc : "Not generated"}
                    >
                      {step.label}
                      {hasContent && activeTab !== step.id && (
                        <span className="ml-1 inline-block h-1.5 w-1.5 rounded-full bg-green-500 align-middle" />
                      )}
                    </button>
                  );
                })}
              </div>

              {/* Active tab content */}
              {activeTab && (
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <h3 className="text-base font-semibold text-gray-900">
                      {STEPS.find((s) => s.id === activeTab)?.label}
                    </h3>
                    <span className="text-xs text-gray-400">
                      — {STEPS.find((s) => s.id === activeTab)?.desc}
                    </span>
                  </div>
                  <SectionContent
                    content={sections[activeTab]}
                    stepLabel={STEPS.find((s) => s.id === activeTab)?.label || activeTab}
                  />
                </div>
              )}
            </div>
          )}

          {/* Empty state */}
          {!streaming && !done && !error && (
            <div className="card flex flex-col items-center justify-center py-16 text-center">
              <SparklesIcon className="h-12 w-12 text-gray-200 mb-4" />
              <h3 className="text-lg font-semibold text-gray-400 mb-2">
                Ready to Run CSRD Analysis
              </h3>
              <p className="text-sm text-gray-400 max-w-sm">
                Fill in the company details and select your ESRS modules on the left,
                then click "Run CSRD Analysis" to start the 8-step AI-powered assessment.
              </p>
              <div className="mt-6 grid grid-cols-2 gap-3 text-left text-xs text-gray-500 max-w-sm w-full">
                {STEPS.map((step, i) => (
                  <div key={step.id} className="flex items-start gap-2">
                    <span className="flex-shrink-0 h-5 w-5 rounded-full bg-gray-100 flex items-center justify-center font-mono text-gray-400">
                      {i + 1}
                    </span>
                    <div>
                      <p className="font-medium text-gray-600">{step.label}</p>
                      <p className="text-gray-400">{step.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
