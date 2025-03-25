import streamlit as st
import pandas as pd
import plotly.graph_objects as go 
import plotly.express as px
from scheduler import *

st.set_page_config(page_title="CPU Scheduler Simulator", layout="wide")

st.markdown("""
    <style>
        h1 { font-size: 50px !important; }
        h3 { font-size: 26px !important; }
        .metric-container { font-size: 22px !important; }
        .stDataFrame { font-size: 18px !important; }
    </style>
""", unsafe_allow_html=True)

st.title("⏱️ SMART CPU SIMULATOR ")
st.markdown("<h3 style='text-align: center;'>Explore different CPU scheduling algorithms and their performance metrics📈</h3>", unsafe_allow_html=True)

# Initialize session state
if 'processes' not in st.session_state:
    st.session_state.processes = []

# Process Input Form
with st.expander("Add New Process", expanded=True):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        pid = st.number_input("Process ID", min_value=1, value=len(st.session_state.processes) + 1)
    with col2:
        arrival = st.number_input("Arrival Time", min_value=0, value=0)
    with col3:
        burst = st.number_input("Burst Time", min_value=1, value=1)
    with col4:
        priority = st.number_input("Priority", min_value=0, value=0)

    if st.button("Add Process", use_container_width=True):
        new_process = Process(pid, arrival, burst, priority)
        st.session_state.processes.append(new_process)
        st.success(f"Process {pid} added successfully!")

# Display Process Table
if st.session_state.processes:
    st.subheader("Process Table")
    process_df = pd.DataFrame(sorted([
        {
            "PID": p.pid,
            "Arrival Time": p.arrival,
            "Burst Time": p.burst,
            "Priority": p.priority
        } for p in st.session_state.processes
    ], key=lambda x: x["PID"], reverse=False))
    st.dataframe(process_df,use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear All Processes", use_container_width=True):
            st.session_state.processes = []
            st.rerun()
    with col2:
        delete_pid = st.selectbox("Select Process to Delete", [p.pid for p in st.session_state.processes])
        if st.button("Delete Selected Process", use_container_width=True):
            st.session_state.processes = [p for p in st.session_state.processes if p.pid != delete_pid]
            st.rerun()
            
# Scheduling Algorithm Selection
st.subheader("Select Scheduling Algorithm")
col1, col2 = st.columns(2)

with col1:
    algorithm = st.selectbox(
        "Algorithm",
        ["FCFS", "SJF (Non-preemptive)", "SRTF (Preemptive)", "Round Robin", "Priority"]
    )

with col2:
    if algorithm == "Priority":
        priority_order = st.radio("Priority Order", ["Lower number = Higher Priority", "Higher number = Higher Priority"])


with col2:
    if algorithm == "Priority":
        priority_order = st.radio("Priority Order", ["Lower number = Higher Priority", "Higher number = Higher Priority"])

    if algorithm == "Round Robin":
        time_quantum = st.number_input("Time Quantum", min_value=1, value=2)

# Run Simulation
if st.session_state.processes and st.button("Run Simulation", use_container_width=True):
    if not st.session_state.processes:
        st.error("Please add processes first!")
    else:
        # Run selected algorithm
        if algorithm == "FCFS":
            processes, gantt_data, switches = fcfs_scheduling(st.session_state.processes)
        elif algorithm == "SJF (Non-preemptive)":
            processes, gantt_data, switches = sjf_scheduling(st.session_state.processes, preemptive=False)
        elif algorithm == "SRTF (Preemptive)":
            processes, gantt_data, switches = sjf_scheduling(st.session_state.processes, preemptive=True)
        elif algorithm == "Round Robin":
            processes, gantt_data, switches = round_robin_scheduling(st.session_state.processes, time_quantum)
        else:  # Priority
            processes, gantt_data, switches = priority_scheduling(st.session_state.processes)

        # Calculate metrics
        avg_turnaround, avg_waiting, avg_response = calculate_metrics(processes)

        processes.sort(key=lambda p: p.pid)

        # Display Gantt Chart
        st.subheader("Gantt Chart")

        # Create figure with secondary y-axis
        fig = go.Figure()

        # Add bars for each process
        for p_id, start, end in gantt_data:
            fig.add_trace(go.Bar(
                x=[end - start],
                y=[f"P{p_id}"],
                orientation='h',
                base=[start],
                marker_color=px.colors.qualitative.Set3[p_id % len(px.colors.qualitative.Set3)],
                name=f"P{p_id}",
                text=f"P{p_id} ({start}-{end})",
                textposition="inside",
                hoverinfo="text",
                showlegend=False
            ))

        # Update layout
        fig.update_layout(
            barmode='overlay',
            xaxis=dict(
                title="Time",
                showgrid=True,
                gridwidth=1,
                gridcolor='LightGray',
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='Black',
            ),
            yaxis=dict(
                title="Process",
                showgrid=True,
                gridwidth=1,
                gridcolor='LightGray',
            ),
            height=50 + (len(st.session_state.processes) * 40),
            margin=dict(l=100, r=100, t=30, b=30),
            plot_bgcolor='white'
        )

        st.plotly_chart(fig, use_container_width=True)

        # Display Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Avg Turnaround Time", f"{avg_turnaround:.2f}")
        with col2:
            st.metric("Avg Waiting Time", f"{avg_waiting:.2f}")
        with col3:
            st.metric("Avg Response Time", f"{avg_response:.2f}")
        with col4:
            st.metric("Context Switches", switches)

        # Process Details Table
        st.subheader("Process Details")
        details_df = pd.DataFrame([
            {
                "PID": p.pid,
                "Completion Time": p.completion_time,
                "Turnaround Time": p.turnaround_time,
                "Waiting Time": p.waiting_time,
                "Response Time": p.response_time
            } for p in processes
        ])
        st.dataframe(details_df)

        # Time Distribution and Time Metrics Visualization
        st.subheader("Process Time Analysis")
        col1, col2 = st.columns(2)

        with col1:
            st.write("Time Distribution")
            time_dist_fig = go.Figure()

            # Add Waiting Time bars
            time_dist_fig.add_trace(go.Bar(
                name='Waiting Time',
                x=[f'P{p.pid}' for p in processes],
                y=[p.waiting_time for p in processes],
                marker_color='#FF9999',  # Light red
                width=0.3
            ))

            # Add Burst Time bars
            time_dist_fig.add_trace(go.Bar(
                name='Burst Time',
                x=[f'P{p.pid}' for p in processes],
                y=[p.burst for p in processes],
                marker_color='#66B2FF',  # Light blue
                width=0.3
            ))

            time_dist_fig.update_layout(
                barmode='stack',
                plot_bgcolor='white',
                bargap=0.4,
                xaxis_title="Process ID",
                yaxis_title="Time",
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            st.plotly_chart(time_dist_fig, use_container_width=True)

        with col2:
            st.write("Time Metrics")
            metrics_fig = go.Figure()

            # Add Response Time bars
            metrics_fig.add_trace(go.Bar(
                name='Response Time',
                x=[f'P{p.pid}' for p in processes],
                y=[p.response_time for p in processes],
                marker_color='#99FF99',  # Light green
                width=0.2
            ))

            # Add Turnaround Time bars
            metrics_fig.add_trace(go.Bar(
                name='Turnaround Time',
                x=[f'P{p.pid}' for p in processes],
                y=[p.turnaround_time for p in processes],
                marker_color='#FFB366',  # Light orange
                width=0.2
            ))

            metrics_fig.update_layout(
                barmode='group',
                plot_bgcolor='white',
                bargap=0.3,
                bargroupgap=0.1,
                xaxis_title="Process ID",
                yaxis_title="Time",
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            st.plotly_chart(metrics_fig, use_container_width=True)