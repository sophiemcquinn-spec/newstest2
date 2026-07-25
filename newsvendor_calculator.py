import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
 
st.set_page_config(page_title="Newsvendor Problem Calculator", layout="centered")
 
st.markdown("# Newsvendor Problem Calculator")
st.markdown("Enter your parameters below to calculate the optimal order quantity.")
st.divider()
st.markdown("### Input Parameters:")

#asking for inputs
col1, col2, col3 = st.columns(3)
with col1:
    P = st.number_input("Selling Price ($)", value=None)
    mean = st.number_input("Average Daily Demand (Units)", value=None)
with col2:
    C = st.number_input("Purchase Cost ($)", value=None)
    std = st.number_input("Standard Deviation of Demand", value=None)
with col3:
    S = st.number_input("Salvage Value ($)", value=None)
    calc = st.button("Calculate", type="primary")

#handling some edge cases
if any(x is None for x in [P, C, S, mean, std]):
    st.warning("Do not leave any parameters blank")
    st.stop()
if P <= C:
    st.error("Selling price must be greater than purchase cost")
    st.stop()
if S >= C:
    st.warning("Salvage value must be less than purchase cost")

#performing the calculation
if calc:
 #empirical q star   
    over = C-S
    under = P-C
    Crit_ratio=under/(under+over)
    Qstar=round(norm.ppf(Crit_ratio,mean,std))
   
  #Monte Carlo q star
    np.random.seed(50)
    trials = 1000000
    qs = range(0, 2*int(mean), 1)
    myprofit = []
    for q in qs:
        demand = np.random.normal(mean, std, trials).clip(0)
        profit = np.minimum(demand, q)*P + np.maximum(0, q-demand)*S - q*C
        myprofit.append(profit.mean())
    mc_qstar = list(qs)[myprofit.index(max(myprofit))]
 
    st.markdown("### Results")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Analytical Q*", f"{Qstar} units")
    with col2:
        st.metric("Monte Carlo Q*", f"{mc_qstar} units")
 
    st.divider()
 
    # ── Formula ────────────────────────────────────────────────────────────────
    st.markdown("## The Math")
    st.markdown(f"""
$$CR = \\frac{{p - c}}{{p - s}} = \\frac{{{P} - {C}}}{{{P} - {S}}} = {cr:.4f}$$
 
$$Q^* = \\mu + z_{{CR}} \\cdot \\sigma = {mean} + {norm.ppf(Crit_ratio):.3f} \\times {std} = {Qstar}$$
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
