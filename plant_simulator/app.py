import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from plant_logic import Crutcher, Dryer, StockTank, NoodleSilo, SigmaMixer, Cascade
from simulation_engine import run_simulation
from ui_inputs import get_crutcher_inputs, get_dryer_inputs, get_tank_inputs, get_simulation_inputs, get_silo_inputs, get_mixer_inputs, get_cascade_inputs
from output_table import format_dataframe_for_display, render_table, export_to_excel

st.set_page_config(page_title="Plant Simulation Dashboard", layout="wide")

st.title("Dynamic Plant Simulation Dashboard")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("Plant Parameters")
    
    crutcher_data = get_crutcher_inputs()
    st.markdown("---")
    
    tank_data = get_tank_inputs()
    st.markdown("---")
    
    silo_data = get_silo_inputs()
    st.markdown("---")
    
    silo_names = [s["name"] for s in silo_data]
    
    dryer_data = get_dryer_inputs(silo_names)
    st.markdown("---")
    
    sim_data = get_simulation_inputs()
    st.markdown("---")
    mixer_data = get_mixer_inputs(silo_names)
    st.markdown("---")
    
    mixer_names = [m["name"] for m in mixer_data]
    cascade_data = get_cascade_inputs(mixer_names)
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    run_btn = col1.button("Run Simulation", type="primary")
    reset_btn = col2.button("Reset")

if reset_btn:
    st.rerun()

if run_btn:
    # 1. Initialize Objects
    crutchers = []
    for cd in crutcher_data:
        crutchers.append(Crutcher(
            name=cd["name"],
            capacity=cd["capacity"],
            cycle_time=cd["cycle_time"],
            efficiency=cd["efficiency"],
            work_hours=cd["work_hours"],
            start_time=cd["start_time"]
        ))
        
    dryers = []
    for dd in dryer_data:
        dryers.append(Dryer(
             name=dd["name"],
             rate_per_hour=dd["rate"],
             efficiency=dd["efficiency"],
             connected_silos=dd["connected_silos"]
        ))
        
    stock_tank = StockTank(
        count=tank_data["num_tanks"],
        capacity_per_tank=tank_data["capacity_per_tank"],
        initial_level_ratio=tank_data["initial_level_ratio"]
    )
    
    silos = []
    for sd in silo_data:
        silos.append(NoodleSilo(
            name=sd["name"],
            capacity=sd["capacity"],
            priority=sd["priority"]
        ))
        
    mixers = []
    for md in mixer_data:
        mixers.append(SigmaMixer(
            name=md["name"],
            input_rate_mt_hr=md["input_rate_mt_hr"],
            efficiency=md["efficiency"],
            connected_silos=md["connected_silos"]
        ))
        
    cascades = []
    for cd in cascade_data:
        cascades.append(Cascade(
            name=cd["name"],
            efficiency=cd["efficiency"],
            connected_mixer=cd["connected_mixer"]
        ))
    
    # 2. Run Simulation
    with st.spinner("Running Simulation..."):
        df, metrics = run_simulation(
             crutchers=crutchers,
             dryers=dryers,
             stock_tank=stock_tank,
             silos=silos,
             mixers=mixers,
             cascades=cascades,
             duration_hours=sim_data["duration_hours"],
             step_minutes=sim_data["step_minutes"],
             dryer_restart_threshold_ratio=sim_data["dryer_restart_threshold"]
        )
        
    # 3. UI Display - Section 1: Summary Dashboard
    st.header("1. Plant Summary Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Production", f"{metrics['Total Production (MT)']} MT")
    m2.metric("Total Consumption", f"{metrics['Total Dryer Consumption (MT)']} MT")
    m3.metric("Min Tank Level", f"{metrics['Minimum Tank Level (MT)']} MT")
    if len(metrics['Dryer Stop Events']) > 0:
        stops_str = ", ".join([f"{time}m" for time in metrics['Dryer Stop Events']])
        st.error(f"⚠️ Dryer Stopped at {stops_str} (Tank ran dry)", icon="🛑")
    else:
        st.success("✅ Dryer Never Stopped", icon="👍")

    st.markdown("---")

    # 4. UI Display - Section 2: Tables
    st.header("2. Simulation Timetable")
    
    df_display = format_dataframe_for_display(df)
    render_table(df_display)
    
    # Download Button
    excel_data = export_to_excel(df_display)
    st.download_button(
        label="Download Excel Report",
        data=excel_data,
        file_name="plant_simulation_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("---")
    
    # 5. UI Display - Section 3: Charts
    st.header("3. Visualization")
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Tank Level Over Time")
        fig_tank = px.line(df, x="TIME (MIN)", y="Tank Level (MT)", title="Stock Tank Sequence", markers=True)
        # add max capacity line
        fig_tank.add_hline(y=stock_tank.total_capacity, line_dash="dash", line_color="red", annotation_text="Max Capacity")
        st.plotly_chart(fig_tank, use_container_width=True)
        
    with c2:
        st.subheader("Production vs Consumption")
        fig_prod = go.Figure()

        # Sum up crutchers for total step production
        crutcher_cols = [col for col in df.columns if "Production (MT)" in col]
        df["Total Production/Step"] = df[crutcher_cols].sum(axis=1)

        # Sum up dryers for total step consumption 
        # (Approximation based on step_minutes for display)
        dryer_cols = [col for col in df.columns if "(MT/HR)" in col]
        step_hours = sim_data["step_minutes"] / 60.0
        df["Total Consumption/Step"] = df[dryer_cols].sum(axis=1) * step_hours

        fig_prod.add_trace(go.Scatter(x=df["TIME (MIN)"], y=df["Total Production/Step"], mode="lines+markers", name="Production (MT/step)"))
        fig_prod.add_trace(go.Scatter(x=df["TIME (MIN)"], y=df["Total Consumption/Step"], mode="lines+markers", name="Consumption (MT/step)", line=dict(dash='dot')))
        
        st.plotly_chart(fig_prod, use_container_width=True)

    st.markdown("---")
    c3, c4 = st.columns(2)
    
    with c3:
        st.subheader("Silo Levels vs Time")
        fig_silos = go.Figure()
        for s in silos:
            fig_silos.add_trace(go.Scatter(x=df["TIME (MIN)"], y=df[f"{s.name} (MT)"], mode="lines", name=s.name))
        fig_silos.update_layout(yaxis_title="Level (MT)")
        st.plotly_chart(fig_silos, use_container_width=True)
        
    with c4:
        st.subheader("Mixer & Cascade Outputs")
        fig_mc = go.Figure()
        for m in mixers:
            fig_mc.add_trace(go.Scatter(x=df["TIME (MIN)"], y=df[f"{m.name} Output (MT)"], mode="lines", name=f"{m.name} Output", line=dict(dash="dot")))
        for c in cascades:
            fig_mc.add_trace(go.Scatter(x=df["TIME (MIN)"], y=df[f"{c.name} Cumulative (MT)"], mode="lines", name=f"{c.name} Cumulative Output", line=dict(width=3)))
        fig_mc.update_layout(yaxis_title="Output (MT)")
        st.plotly_chart(fig_mc, use_container_width=True)
    
else:
    st.info("👈 Set your plant parameters in the sidebar and click **Run Simulation** to generate the dashboard report.")
