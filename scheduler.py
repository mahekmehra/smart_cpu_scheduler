
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

def priority_scheduling(processes: List[Process]) -> Tuple[List[Process], List[tuple], int]:
    processes = sorted(processes, key=lambda x: (x.priority, x.arrival))
    return fcfs_scheduling(processes)