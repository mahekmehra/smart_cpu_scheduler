
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class Process:
    pid: int
    arrival: int
    burst: int
    priority: int = 0
    remaining_burst: Optional[int] = None
    completion_time: int = 0
    turnaround_time: int = 0
    waiting_time: int = 0
    response_time: int = -1

    def __post_init__(self):
        self.remaining_burst = self.burst

def calculate_metrics(processes: List[Process]):
    avg_turnaround = np.mean([p.turnaround_time for p in processes])
    avg_waiting = np.mean([p.waiting_time for p in processes])
    avg_response = np.mean([p.response_time for p in processes])
    return avg_turnaround, avg_waiting, avg_response

def fcfs_scheduling(processes: List[Process]) -> Tuple[List[Process], List[tuple], int]:
    processes = sorted(processes, key=lambda x: x.arrival)
    current_time = 0
    gantt_data = []
    context_switches = 0

    for process in processes:
        if current_time < process.arrival:
            current_time = process.arrival

        if process.response_time == -1:
            process.response_time = current_time - process.arrival

        process.waiting_time = current_time - process.arrival
        process.completion_time = current_time + process.burst
        process.turnaround_time = process.completion_time - process.arrival
        gantt_data.append((process.pid, current_time, process.completion_time))
        current_time = process.completion_time
        context_switches += 1

    return processes, gantt_data, context_switches - 1

def sjf_scheduling(processes: List[Process], preemptive: bool = False) -> Tuple[List[Process], List[tuple], int]:
    processes = [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    current_time = 0
    completed = []
    gantt_data = []
    context_switches = 0

    while processes:
        available = [p for p in processes if p.arrival <= current_time]

        if not available:
            current_time = min(p.arrival for p in processes)
            continue

        if preemptive:
            process = min(available, key=lambda x: x.remaining_burst or float('inf'))
            if process.response_time == -1:
                process.response_time = current_time - process.arrival

            execution_time = 1
            if process.remaining_burst:
                process.remaining_burst -= execution_time
            gantt_data.append((process.pid, current_time, current_time + execution_time))
            current_time += execution_time

            if process.remaining_burst == 0:
                process.completion_time = current_time
                process.turnaround_time = process.completion_time - process.arrival
                process.waiting_time = process.turnaround_time - process.burst
                completed.append(process)
                processes.remove(process)
                context_switches += 1
        else:
            process = min(available, key=lambda x: x.burst)
            if process.response_time == -1:
                process.response_time = current_time - process.arrival

            process.completion_time = current_time + process.burst
            process.turnaround_time = process.completion_time - process.arrival
            process.waiting_time = process.turnaround_time - process.burst
            gantt_data.append((process.pid, current_time, process.completion_time))
            current_time = process.completion_time
            completed.append(process)
            processes.remove(process)
            context_switches += 1

    return completed, gantt_data, context_switches - 1

def round_robin_scheduling(processes: List[Process], time_quantum: int) -> Tuple[List[Process], List[tuple], int]:
    processes = [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    current_time = 0
    completed = []
    gantt_data = []
    context_switches = 0
    queue = []

    while processes or queue:
        while processes and processes[0].arrival <= current_time:
            queue.append(processes.pop(0))

        if not queue:
            current_time = processes[0].arrival if processes else current_time
            continue

        process = queue.pop(0)

        if process.response_time == -1:
            process.response_time = current_time - process.arrival

        execution_time = min(time_quantum, process.remaining_burst or 0)
        if process.remaining_burst:
            process.remaining_burst -= execution_time
        gantt_data.append((process.pid, current_time, current_time + execution_time))
        current_time += execution_time
        context_switches += 1

        while processes and processes[0].arrival <= current_time:
            queue.append(processes.pop(0))

        if process.remaining_burst and process.remaining_burst > 0:
            queue.append(process)
        else:
            process.completion_time = current_time
            process.turnaround_time = process.completion_time - process.arrival
            process.waiting_time = process.turnaround_time - process.burst
            completed.append(process)

    return completed, gantt_data, context_switches - 1

def priority_scheduling(processes: List[Process], ascending: bool = True) -> Tuple[List[Process], List[tuple], int]:
    """
    Implements Preemptive Priority Scheduling.
    The user specifies whether lower numbers indicate higher priority (ascending=True) or vice versa.
    """
    # Define sorting order based on user input
    priority_sort_order = (lambda p: p.priority) if ascending else (lambda p: -p.priority)

    # Sort processes by arrival time first
    processes = sorted(processes, key=lambda x: x.arrival)
    
    time = 0
    gantt_chart = []
    completed = []
    ready_queue = []
    remaining_burst = {p.pid: p.burst for p in processes}
    context_switches = 0
    last_pid = None  # Track the last executed process

    while len(completed) < len(processes):
        # Add processes that have arrived to the queue
        for p in processes:
            if p.arrival <= time and p not in ready_queue and p.pid not in [c.pid for c in completed]:
                ready_queue.append(p)

        if ready_queue:
            # Sort queue based on user-defined priority order
            ready_queue.sort(key=priority_sort_order)
            current_process = ready_queue[0]

            # If a different process is executed, increase context switch count
            if last_pid is not None and last_pid != current_process.pid:
                context_switches += 1

            # Run process for 1 unit time (preemptive execution)
            gantt_chart.append((current_process.pid, time, time + 1))
            remaining_burst[current_process.pid] -= 1
            last_pid = current_process.pid
            time += 1

            # If process is completed, update its metrics
            if remaining_burst[current_process.pid] == 0:
                current_process.completion_time = time
                current_process.turnaround_time = current_process.completion_time - current_process.arrival
                current_process.waiting_time = current_process.turnaround_time - current_process.burst
                completed.append(current_process)
                ready_queue.remove(current_process)
        else:
            time += 1  # If no process is ready, move forward in time

    return completed, gantt_chart, context_switches
