import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
 
st.set_page_config(page_title="Newsvendor Calculator", layout="centered")
 
st.markdown("# 📰 Newsvendor Problem Calculator")
st.markdown("Enter your parameters below to calculate the optimal order quantity.")
st.divider()
 
# ── Inputs ─────────────────────────────────────────────────────────────────────
st.markdown("## Parameters")
 
col1, col2, col3 = st.columns(3)
with col1:
    P = st.number_input("Selling Price ($)", min_value=0.01, value=1.50, step=0.01)
    mean = st.number_input("Average Daily Demand", min_value=1, value=100, step=1)
with col2:
    C = st.number_input("Purchase Cost ($)", min_value=0.01, value=0.75, step=0.01)
    std = st.number_input("Std Deviation of Demand", min_value=1, value=25, step=1)
with col3:
    S = st.number_input("Salvage Value ($)", min_value=0.00, value=0.10, step=0.01)
    trials = st.number_input("Monte Carlo Trials", min_value=100, value=100000, step=1000)
 
st.divider()
 
if P <= C:
    st.error("Selling price must be greater than purchase cost.")
    st.stop()
if S >= C:
    st.warning("Salvage value should be less than purchase cost.")
 
# ── Calculate ──────────────────────────────────────────────────────────────────
if st.button("Calculate", type="primary"):
 
    # Analytical Q*
    overage  = C - S
    underage = P - C
    cr       = underage / (underage + overage)
    Qstar    = round(norm.ppf(cr, mean, std))
 
    # Monte Carlo Q*
    np.random.seed(42)
    qs = range(0, 200, 1)
    myprofit = []
    for q in qs:
        demand = np.random.normal(mean, std, trials).clip(0)
        profit = np.minimum(demand, q)*P + np.maximum(0, q-demand)*S - q*C
        myprofit.append(profit.mean())
    mc_qstar = list(qs)[myprofit.index(max(myprofit))]
 
    # ── Results ────────────────────────────────────────────────────────────────
    st.markdown("## Results")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Critical Ratio", f"{cr:.4f}")
    with col2:
        st.metric("Analytical Q*", f"{Qstar} units")
    with col3:
        st.metric("Monte Carlo Q*", f"{mc_qstar} units")
 
    st.divider()
 
    # ── Formula ────────────────────────────────────────────────────────────────
    st.markdown("## The Math")
    st.markdown(f"""
$$CR = \\frac{{p - c}}{{p - s}} = \\frac{{{P} - {C}}}{{{P} - {S}}} = {cr:.4f}$$
 
$$Q^* = \\mu + z_{{CR}} \\cdot \\sigma = {mean} + {norm.ppf(cr):.3f} \\times {std} = {Qstar}$$
""")
 
    st.divider()
 
    # ── Plot ───────────────────────────────────────────────────────────────────
    st.markdown("## Expected Profit vs. Order Quantity")
 
    fig = go.Figure()
    fig.add_scatter(
        x=list(qs),
        y=myprofit,
        mode='lines',
        name='Expected Profit',
        line=dict(color='steelblue', width=2)
    )
    fig.add_vline(
        x=mc_qstar, line_dash='dash', line_color='red',
        annotation_text=f'MC Q*={mc_qstar}',
        annotation_position='top left'
    )
    fig.add_vline(
        x=Qstar, line_dash='dash', line_color='green',
        annotation_text=f'Analytical Q*={Qstar}',
        annotation_position='top right'
    )
    fig.update_layout(
        title=f'Expected Profit vs. Order Quantity ({trials:,} trials)',
        xaxis_title='Order Quantity',
        yaxis_title='Expected Profit ($)',
        plot_bgcolor='white',
        height=450
    )
    fig.update_yaxes(gridcolor='#eee', tickprefix='$')
    fig.update_xaxes(gridcolor='#eee')
    st.plotly_chart(fig, use_container_width=True)
 
    st.success(f"At Q*={mc_qstar}, the Monte Carlo and analytical solutions "
               f"{'agree.' if mc_qstar == Qstar else f'differ by {abs(mc_qstar - Qstar)} unit(s).'}")
