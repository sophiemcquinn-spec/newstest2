import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm

st.set_page_config(page_title="Newsvendor Calculator", layout="centered")

st.markdown("# 📰 Newsvendor Problem Calculator")
st.markdown("Enter your problem parameters below to calculate the optimal order quantity.")
st.divider()

# ── Parameter Inputs ───────────────────────────────────────────────────────────
st.markdown("## Parameters")

col1, col2, col3 = st.columns(3)
with col1:
    P = st.number_input("Selling Price ($)", min_value=0.01, value=1.50, step=0.01)
    mu = st.number_input("Average Daily Demand", min_value=1, value=100, step=1)
with col2:
    C = st.number_input("Purchase Cost ($)", min_value=0.01, value=0.75, step=0.01)
    sigma = st.number_input("Std Deviation of Demand", min_value=1, value=25, step=1)
with col3:
    S = st.number_input("Salvage Value ($)", min_value=0.00, value=0.10, step=0.01)
    trials = st.selectbox("Monte Carlo Trials", [10000, 50000, 100000], index=0)

st.divider()

# ── Validation ─────────────────────────────────────────────────────────────────
if P <= C:
    st.error("Selling price must be greater than purchase cost.")
    st.stop()
if S >= C:
    st.warning("Salvage value is unusually high — are you sure it exceeds purchase cost?")

# ── Calculate Button ───────────────────────────────────────────────────────────
if st.button("Calculate Optimal Order Quantity", type="primary"):

    # Analytical solution
    overage  = C - S
    underage = P - C
    CR       = underage / (underage + overage)
    Q_analytical = round(norm.ppf(CR, mu, sigma))

    # Monte Carlo solution
    qs = range(max(1, mu - 4*sigma), mu + 4*sigma, 1)
    mc_profits = []
    for q in qs:
        demands = np.random.normal(mu, sigma, trials).clip(0)
        profits = np.minimum(demands, q)*P + np.maximum(0, q-demands)*S - q*C
        mc_profits.append(profits.mean())
    Q_mc = list(qs)[mc_profits.index(max(mc_profits))]
    max_profit = max(mc_profits)

    # ── Results ────────────────────────────────────────────────────────────────
    st.markdown("## Results")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Critical Ratio", f"{CR:.4f}")
    with col2:
        st.metric("Analytical Q*", f"{Q_analytical} units")
    with col3:
        st.metric("Monte Carlo Q*", f"{Q_mc} units")

    st.divider()

    # ── Explanation ────────────────────────────────────────────────────────────
    st.markdown("## The Math")
    st.markdown(f"""
The **Critical Ratio** tells us what fraction of demand days we should be able to cover:

$$CR = \\frac{{p - c}}{{p - s}} = \\frac{{{P} - {C}}}{{{P} - {S}}} = {CR:.4f}$$

This means we should stock enough to meet demand on **{CR*100:.1f}%** of days.

Using the inverse normal CDF:

$$Q^* = \\mu + z_{{CR}} \\cdot \\sigma = {mu} + {norm.ppf(CR):.3f} \\times {sigma} = {Q_analytical}$$
""")

    st.divider()

    # ── Monte Carlo Chart ──────────────────────────────────────────────────────
    st.markdown("## Monte Carlo Simulation")
    st.markdown(f"Expected daily profit simulated across **{trials:,} trials** for each possible order quantity:")

    fig = go.Figure()
    fig.add_scatter(
        x=list(qs), y=mc_profits,
        mode="lines", name="Expected Profit",
        line=dict(color="#1f77b4", width=2)
    )
    fig.add_vline(
        x=Q_mc, line_dash="dash", line_color="#2ca02c",
        annotation_text=f"MC Q*={Q_mc}",
        annotation_position="top right"
    )
    fig.add_vline(
        x=Q_analytical, line_dash="dot", line_color="#ff7f0e",
        annotation_text=f"Analytical Q*={Q_analytical}",
        annotation_position="top left"
    )
    fig.update_layout(
        title=f"Expected Daily Profit vs. Order Quantity ({trials:,} trials)",
        xaxis_title="Order Quantity",
        yaxis_title="Expected Daily Profit ($)",
        plot_bgcolor="white",
        height=400,
        legend=dict(orientation="h", y=1.12)
    )
    fig.update_yaxes(gridcolor="#eee", tickprefix="$")
    fig.update_xaxes(gridcolor="#eee")
    st.plotly_chart(fig, use_container_width=True)

    st.success(f"At the optimal order quantity of **{Q_mc} units**, expected daily profit is **${max_profit:.2f}**.")
