import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { companyAPI } from "../../api/client";
import toast from "react-hot-toast";
import { BuildingOfficeIcon } from "@heroicons/react/24/outline";

const EU_COUNTRIES = [
  "Austria","Belgium","Bulgaria","Croatia","Cyprus","Czech Republic","Denmark",
  "Estonia","Finland","France","Germany","Greece","Hungary","Ireland","Italy",
  "Latvia","Lithuania","Luxembourg","Malta","Netherlands","Poland","Portugal",
  "Romania","Slovakia","Slovenia","Spain","Sweden","United Kingdom","Switzerland",
  "Norway","Liechtenstein","Iceland",
];

const SECTORS = [
  "Agriculture","Automotive","Aviation","Chemicals","Coal","Construction",
  "Consumer Staples","Energy","Financial Services","Food & Beverage",
  "Healthcare","Information Technology","Insurance","Manufacturing",
  "Media & Entertainment","Mining","Oil & Gas","Pharmaceuticals",
  "Real Estate","Retail","Steel & Metals","Telecommunications",
  "Textiles & Apparel","Tourism","Transportation","Utilities","Other",
];

export default function CompanySettings() {
  const qc = useQueryClient();
  const [form, setForm] = useState({});

  const { data: company, isLoading } = useQuery({
    queryKey: ["company"],
    queryFn: () => companyAPI.get().then((r) => r.data),
    onError: () => {},
  });

  useEffect(() => {
    if (company) setForm(company);
  }, [company]);

  const updateMutation = useMutation({
    mutationFn: (data) => companyAPI.update(data),
    onSuccess: () => {
      qc.invalidateQueries(["company"]);
      toast.success("Company profile updated");
    },
    onError: () => toast.error("Failed to update company profile"),
  });

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setForm((f) => ({
      ...f,
      [name]: type === "number" ? (value === "" ? "" : parseFloat(value)) : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    updateMutation.mutate(form);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Company Profile</h1>
        <p className="text-gray-500 text-sm mt-1">
          Used in all CSRD reports and XBRL filings
        </p>
      </div>

      {isLoading ? (
        <div className="card animate-pulse h-64" />
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Identity */}
          <div className="card space-y-4">
            <div className="flex items-center gap-3 mb-2">
              <BuildingOfficeIcon className="h-5 w-5 text-blue-700" />
              <h2 className="font-semibold text-gray-800">Company Identity</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Company Name *</label>
                <input name="name" className="input" value={form.name || ""} onChange={handleChange} required />
              </div>
              <div>
                <label className="label">Legal Name</label>
                <input name="legal_name" className="input" value={form.legal_name || ""} onChange={handleChange}
                  placeholder="Full legal registered name" />
              </div>
              <div>
                <label className="label">Registration Number</label>
                <input name="registration_number" className="input" value={form.registration_number || ""}
                  onChange={handleChange} placeholder="Company registration number" />
              </div>
              <div>
                <label className="label">LEI Code</label>
                <input name="lei_code" className="input" value={form.lei_code || ""}
                  onChange={handleChange} placeholder="20-character LEI" maxLength={20} />
              </div>
              <div>
                <label className="label">Website</label>
                <input name="website" type="url" className="input" value={form.website || ""}
                  onChange={handleChange} placeholder="https://..." />
              </div>
              <div>
                <label className="label">Sustainability Contact Email</label>
                <input name="sustainability_contact_email" type="email" className="input"
                  value={form.sustainability_contact_email || ""} onChange={handleChange} />
              </div>
            </div>
          </div>

          {/* Classification */}
          <div className="card space-y-4">
            <h2 className="font-semibold text-gray-800">Industry Classification</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Sector</label>
                <select name="sector" className="input" value={form.sector || ""} onChange={handleChange}>
                  <option value="">Select sector…</option>
                  {SECTORS.map((s) => <option key={s}>{s}</option>)}
                </select>
              </div>
              <div>
                <label className="label">NACE Code</label>
                <input name="nace_code" className="input" value={form.nace_code || ""}
                  onChange={handleChange} placeholder="e.g., C29.1" />
              </div>
              <div>
                <label className="label">Country of Headquarters</label>
                <select name="country" className="input" value={form.country || ""} onChange={handleChange}>
                  <option value="">Select country…</option>
                  {EU_COUNTRIES.map((c) => <option key={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label className="label">Reporting Year</label>
                <select name="reporting_year" className="input"
                  value={form.reporting_year || new Date().getFullYear()} onChange={handleChange}>
                  {[2022, 2023, 2024, 2025, 2026].map((y) => (
                    <option key={y} value={y}>{y}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Size */}
          <div className="card space-y-4">
            <h2 className="font-semibold text-gray-800">Company Size</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="label">Employees (FTE)</label>
                <input name="employee_count" type="number" className="input"
                  value={form.employee_count || ""} onChange={handleChange} placeholder="e.g., 5000" />
              </div>
              <div>
                <label className="label">Annual Revenue (EUR M)</label>
                <input name="annual_revenue" type="number" step="0.1" className="input"
                  value={form.annual_revenue || ""} onChange={handleChange} placeholder="e.g., 500.0" />
              </div>
              <div>
                <label className="label">Total Assets (EUR M)</label>
                <input name="total_assets" type="number" step="0.1" className="input"
                  value={form.total_assets || ""} onChange={handleChange} placeholder="e.g., 1200.0" />
              </div>
            </div>
            <p className="text-xs text-gray-400">
              CSRD applies to: large companies (&gt;500 employees or &gt;EUR 40M revenue and &gt;EUR 20M total assets)
            </p>
          </div>

          <div className="flex justify-end gap-3">
            <button type="button" className="btn-secondary"
              onClick={() => setForm(company || {})}>Reset</button>
            <button type="submit" className="btn-primary" disabled={updateMutation.isPending}>
              {updateMutation.isPending ? "Saving…" : "Save Changes"}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
