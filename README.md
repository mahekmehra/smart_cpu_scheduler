⏱️ SMART CPU SCHEDULER SIMULATOR

Overview :-

SMART CPU Scheduler Simulator is a real-time, interactive web-based application that simulates various CPU scheduling algorithms. Built using Streamlit and Plotly, this tool allows users to visualize scheduling processes dynamically and analyze performance metrics.

Features :-

  -> Supports Multiple Scheduling Algorithms:
  -> First Come First Serve (FCFS)
  -> Shortest Job First (SJF) - Non-preemptive
  -> Shortest Remaining Time First (SRTF) - Preemptive
  -> Round Robin (RR)
  -> Priority Scheduling (Ascending/Descending)

User-Friendly Input System :-

  -> Add, delete, and modify process details
  -> Customize priority and time quantum for respective algorithms

Dynamic Visualization :-

  -> Gantt Chart for process execution order
  -> Process Table to track execution metrics
  -> Time Distribution Analysis
  -> Performance Metrics (TAT, WT, RT, Context Switches)

Modern UI/UX :-

  -> Responsive design with a dark theme
  -> Streamlined process interaction
  -> User friendly view and aligned UI elements for better readability

Tech Stack :-

  -> Frontend & Backend: Streamlit
  -> Data Handling: Pandas
  -> Visualization: Plotly
  -> Programming Language: Python 3

Usage :-

1> Add Processes: Enter Process ID, Arrival Time, Burst Time, and Priority.
2> Select Scheduling Algorithm: Choose one of the five available options.
3> Set Parameters:
   -> Priority Scheduling: Choose ascending or descending order.
   -> Round Robin: Set time quantum.
4> Run Simulation: Click the Run Simulation button to visualize execution.
5> Analyze Results:
   -> View the Gantt Chart for execution order.
   -> Study Process Details Table for TAT, WT, and RT.
6> Analyze Performance Metrics.

Performance Metrics Explained :-

  -> Turnaround Time (TAT) = Completion Time - Arrival Time
  -> Waiting Time (WT) = TAT - Burst Time
  -> Response Time (RT) = First CPU Allocation - Arrival Time
  -> Context Switches = Number of times CPU switches between processes

