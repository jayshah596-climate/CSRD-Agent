import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authAPI } from "../../api/client";
import useAuthStore from "../../store/authStore";
import toast from "react-hot-toast";

export default function Register() {
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    company_name: "",
  });
  const [loading, setLoading] = useState(false);
  const { setAuth } = useAuthStore();
  const navigate = useNavigate();

  const handleChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.password.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }
    setLoading(true);
    try {
      const { data } = await authAPI.register(form);
      setAuth(data.user, data.access_token);
      toast.success("Account created successfully!");
      navigate("/dashboard");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-950 via-blue-900 to-green-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-white shadow-lg mb-4">
            <span className="text-blue-900 font-bold text-2xl">CA</span>
          </div>
          <h1 className="text-3xl font-bold text-white">CSRD Agent</h1>
          <p className="text-blue-200 mt-1">Start your ESRS 2025 compliance journey</p>
        </div>

        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Create account</h2>
          <p className="text-gray-500 text-sm mb-6">Free forever. No credit card required.</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Full name</label>
              <input
                name="full_name"
                type="text"
                className="input"
                placeholder="Jane Smith"
                value={form.full_name}
                onChange={handleChange}
                required
              />
            </div>
            <div>
              <label className="label">Work email</label>
              <input
                name="email"
                type="email"
                className="input"
                placeholder="jane@company.com"
                value={form.email}
                onChange={handleChange}
                required
              />
            </div>
            <div>
              <label className="label">Company name</label>
              <input
                name="company_name"
                type="text"
                className="input"
                placeholder="Acme Corp"
                value={form.company_name}
                onChange={handleChange}
              />
            </div>
            <div>
              <label className="label">Password</label>
              <input
                name="password"
                type="password"
                className="input"
                placeholder="Min 8 characters"
                value={form.password}
                onChange={handleChange}
                required
                minLength={8}
              />
            </div>

            <button type="submit" className="btn-primary w-full py-2.5" disabled={loading}>
              {loading ? "Creating account..." : "Create free account"}
            </button>
          </form>

          <p className="mt-4 text-xs text-gray-400 text-center">
            By signing up you agree to our Terms of Service and Privacy Policy.
          </p>

          <div className="mt-4 text-center">
            <p className="text-sm text-gray-500">
              Already have an account?{" "}
              <Link to="/login" className="text-blue-700 font-medium hover:text-blue-800">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
