"use client";

import * as React from "react";

interface PlanLimit {
  maxUsers: number;
  maxAgents: number;
  voice: boolean;
  whatsapp: boolean;
  analytics: boolean;
  apiLimit: string;
}

interface Plan {
  name: string;
  code: string;
  priceMonthly: number;
  currency: string;
  description: string;
  limits: PlanLimit;
}

interface Invoice {
  id: string;
  number: string;
  amount: number;
  status: string;
  date: string;
}

export default function BillingPage() {
  const plans: Plan[] = [
    {
      name: "Free Tier",
      code: "free",
      priceMonthly: 0,
      currency: "USD",
      description: "Sandbox developer environment",
      limits: { maxUsers: 2, maxAgents: 1, voice: false, whatsapp: false, analytics: false, apiLimit: "500" },
    },
    {
      name: "Starter Plan",
      code: "starter",
      priceMonthly: 29,
      currency: "USD",
      description: "Perfect for single clinics or shops",
      limits: { maxUsers: 5, maxAgents: 3, voice: True, whatsapp: false, analytics: True, apiLimit: "5,000" },
    },
    {
      name: "Professional Plan",
      code: "professional",
      priceMonthly: 79,
      currency: "USD",
      description: "Standard production grade workflows",
      limits: { maxUsers: 20, maxAgents: 10, voice: True, whatsapp: True, analytics: True, apiLimit: "50,000" },
    },
    {
      name: "Business Plan",
      code: "business",
      priceMonthly: 199,
      currency: "USD",
      description: "Advanced channels & team collaboration",
      limits: { maxUsers: 50, maxAgents: 25, voice: True, whatsapp: True, analytics: True, apiLimit: "200,000" },
    },
  ];

  // Current active subscription state
  const [activePlanCode, setActivePlanCode] = React.useState("starter");
  const [showCheckoutModal, setShowCheckoutModal] = React.useState(false);
  const [selectedCheckoutPlan, setSelectedCheckoutPlan] = React.useState<Plan | null>(null);
  
  // Checkout coupon input
  const [couponCode, setCouponCode] = React.useState("");
  const [discountValue, setDiscountValue] = React.useState(0); // in percent
  const [couponApplied, setCouponApplied] = React.useState(false);

  // Mock invoice history
  const [invoices] = React.useState<Invoice[]>([
    { id: "1", number: "INV-202607-F1E93", amount: 29.0, status: "paid", date: "2026-07-01" },
    { id: "2", number: "INV-202606-B81C9", amount: 29.0, status: "paid", date: "2026-06-01" },
  ]);

  // Usage telemetry metrics state
  const usageStats = [
    { label: "AI Requests", consumed: 345, limit: 1000, unit: "calls" },
    { label: "Voice Minutes", consumed: 45, limit: 150, unit: "mins" },
    { label: "Storage Space", consumed: 120, limit: 500, unit: "MB" },
    { label: "Teammates Slots", consumed: 3, limit: 5, unit: "users" },
  ];

  const handleApplyCoupon = (e: React.FormEvent) => {
    e.preventDefault();
    if (couponCode.toUpperCase() === "NEXORA20") {
      setDiscountValue(20);
      setCouponApplied(true);
    } else {
      alert("Invalid coupon code!");
    }
  };

  const handleConfirmCheckout = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedCheckoutPlan) {
      setActivePlanCode(selectedCheckoutPlan.code);
      setShowCheckoutModal(false);
      setCouponCode("");
      setDiscountValue(0);
      setCouponApplied(false);
    }
  };

  return (
    <div className="space-y-10 animate-in fade-in duration-300">
      
      {/* Title */}
      <div className="space-y-1">
        <h2 className="text-3xl font-extrabold tracking-tight">Billing & Subscriptions</h2>
        <p className="text-sm text-muted-foreground font-semibold">
          Manage pricing packages, look up invoice history, and monitor usage limits
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Side: Current Plan & Usage Metrics */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Active plan card */}
          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4">
            <h3 className="text-lg font-bold">Subscription Status</h3>
            <div className="p-5 rounded-xl border border-border/80 bg-background/50 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-foreground capitalize">
                    {plans.find((p) => p.code === activePlanCode)?.name}
                  </span>
                  <span className="text-[10px] font-extrabold bg-green-500/10 text-green-500 px-2.5 py-0.5 rounded-xl">
                    Active
                  </span>
                </div>
                <p className="text-xs text-muted-foreground">Next billing date is August 1, 2026 via Stripe</p>
              </div>
              <button
                onClick={() => {
                  if (confirm("Are you sure you want to cancel subscription scheduled at period end?")) {
                    alert("Subscription cancellation scheduled!");
                  }
                }}
                className="text-xs text-red-500 hover:text-red-600 font-bold border border-red-500/30 hover:bg-red-500/10 px-4 py-2 rounded-xl transition-all cursor-pointer"
              >
                Cancel Subscription
              </button>
            </div>
          </div>

          {/* Usage indicators */}
          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4">
            <h3 className="text-lg font-bold">Usage Telemetry Quotas</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {usageStats.map((stat, i) => {
                const percent = Math.min(100, Math.round((stat.consumed / stat.limit) * 100));
                return (
                  <div key={i} className="space-y-2">
                    <div className="flex items-center justify-between text-xs font-semibold">
                      <span className="text-muted-foreground">{stat.label}</span>
                      <span className="text-foreground">
                        {stat.consumed} / {stat.limit} {stat.unit}
                      </span>
                    </div>
                    {/* Progress Bar Container */}
                    <div className="h-2 w-full rounded-full bg-muted/60 overflow-hidden">
                      <div
                        className="h-full bg-primary rounded-full transition-all duration-500"
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Invoices list */}
          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4">
            <h3 className="text-lg font-bold">Invoice History</h3>
            <div className="overflow-hidden rounded-xl border border-border bg-background/30">
              <table className="w-full border-collapse text-left text-sm">
                <thead>
                  <tr className="border-b border-border bg-muted/20">
                    <th className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px]">Invoice ID</th>
                    <th className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px]">Billing Date</th>
                    <th className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px]">Amount</th>
                    <th className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px]">Status</th>
                    <th className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px] text-right">PDF</th>
                  </tr>
                </thead>
                <tbody>
                  {invoices.map((inv) => (
                    <tr key={inv.id} className="border-b border-border/40 last:border-0 text-xs">
                      <td className="p-3 font-mono font-semibold">{inv.number}</td>
                      <td className="p-3">{inv.date}</td>
                      <td className="p-3">${inv.amount.toFixed(2)}</td>
                      <td className="p-3">
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-xl bg-green-500/10 text-green-500">
                          {inv.status}
                        </span>
                      </td>
                      <td className="p-3 text-right">
                        <button
                          onClick={() => alert("Downloading PDF Invoice...")}
                          className="text-[10px] text-primary font-bold hover:underline cursor-pointer"
                        >
                          Download
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>

        {/* Pricing List Cards */}
        <div className="space-y-6">
          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4">
            <h3 className="text-lg font-bold">Subscription Options</h3>
            <div className="space-y-4">
              {plans.map((plan) => {
                const isCurrent = plan.code === activePlanCode;
                return (
                  <div
                    key={plan.code}
                    className={`p-4 rounded-xl border transition-all ${
                      isCurrent
                        ? "border-primary bg-primary/5 shadow-md"
                        : "border-border bg-background/30 hover:border-border/80"
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="space-y-1">
                        <h4 className="text-xs font-extrabold">{plan.name}</h4>
                        <p className="text-[10px] text-muted-foreground leading-normal">{plan.description}</p>
                      </div>
                      <div className="text-right">
                        <span className="text-sm font-extrabold">${plan.priceMonthly}</span>
                        <span className="text-[10px] text-muted-foreground block">/mo</span>
                      </div>
                    </div>

                    <div className="mt-4 pt-3 border-t border-border/40 grid grid-cols-2 gap-2 text-[10px] text-muted-foreground font-mono">
                      <span>Users: {plan.limits.maxUsers}</span>
                      <span>Agents: {plan.limits.maxAgents}</span>
                      <span>Voice: {plan.limits.voice ? "Yes" : "No"}</span>
                      <span>WhatsApp: {plan.limits.whatsapp ? "Yes" : "No"}</span>
                    </div>

                    {!isCurrent && (
                      <button
                        onClick={() => {
                          setSelectedCheckoutPlan(plan);
                          setShowCheckoutModal(true);
                        }}
                        className="mt-4 w-full py-2 bg-primary text-primary-foreground hover:bg-primary/95 text-[10px] font-bold rounded-xl transition-all cursor-pointer"
                      >
                        Upgrade Plan
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

      </div>

      {/* Checkout Wizard Modal */}
      {showCheckoutModal && selectedCheckoutPlan && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
          <div className="bg-card border border-border rounded-3xl p-8 max-w-md w-full shadow-2xl space-y-6">
            <div className="text-center space-y-2">
              <h3 className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                CHECKOUT SUBSCRIPTION
              </h3>
              <p className="text-sm text-muted-foreground font-semibold">
                Confirm payment method to active the {selectedCheckoutPlan.name}
              </p>
            </div>

            <div className="p-4 rounded-xl bg-muted/20 border border-border/60 flex items-center justify-between text-xs">
              <span className="font-semibold text-muted-foreground">Billing Price:</span>
              <span className="font-extrabold text-foreground">
                ${(couponApplied ? selectedCheckoutPlan.priceMonthly * (1 - discountValue / 100) : selectedCheckoutPlan.priceMonthly).toFixed(2)} USD
              </span>
            </div>

            <form onSubmit={handleConfirmCheckout} className="space-y-4">
              
              {/* Payment Token */}
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Credit Card Number</label>
                <input
                  type="text"
                  required
                  placeholder="4242 4242 4242 4242"
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all font-mono"
                />
              </div>

              {/* Coupons form */}
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Promo Coupon</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={couponCode}
                    onChange={(e) => setCouponCode(e.target.value)}
                    placeholder="e.g. NEXORA20"
                    className="flex-1 px-3 py-2 rounded-xl border border-border bg-background/50 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all font-mono uppercase"
                  />
                  <button
                    type="button"
                    onClick={handleApplyCoupon}
                    className="px-3.5 py-2 border border-border text-foreground hover:bg-muted font-bold text-[10px] rounded-xl transition-all cursor-pointer"
                  >
                    Apply
                  </button>
                </div>
                {couponApplied && (
                  <p className="text-[10px] text-green-500 font-bold">✓ Coupon code applied: {discountValue}% discount</p>
                )}
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setShowCheckoutModal(false);
                    setCouponCode("");
                    setDiscountValue(0);
                    setCouponApplied(false);
                  }}
                  className="flex-1 py-2.5 border border-border text-foreground font-semibold text-xs rounded-xl hover:bg-muted transition-all cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-primary text-primary-foreground font-bold text-xs rounded-xl hover:bg-primary/90 transition-all cursor-pointer"
                >
                  Confirm & Active
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
