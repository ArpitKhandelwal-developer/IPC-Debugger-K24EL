# analyzer.py
import time


# ---- Detector Functions ----

def detect_queue_backlog(traces, threshold=50):
    # scans traces for queue_put/queue_get imbalance
    puts = 0
    gets = 0
    for t in list(traces):
        if t['type'] == 'queue_put':
            puts += 1
        if t['type'] == 'queue_get':
            gets += 1
    backlog = puts - gets
    alerts = []
    if backlog > threshold:
        alerts.append({
            'issue': 'queue_backlog',
            'backlog': backlog,
            'severity': 'high',
            'time': time.time()
        })
    return alerts


def detect_pipe_latency(traces, latency_ms_threshold=500):
    alerts = []
    for t in list(traces):
        if t['type'] == 'pipe_message':
            sent = t['meta'].get('sent_ts')
            recv = t['meta'].get('rcv_ts')
            if sent and recv:
                d = (recv - sent) * 1000
                if d > latency_ms_threshold:
                    alerts.append({
                        'issue': 'pipe_high_latency',
                        'latency_ms': d,
                        'label': t['label'],
                        'time': time.time()
                    })
    return alerts


def detect_deadlock(traces, processes, window_s=5):
    now = time.time()
    recent = [t for t in list(traces) if now - t['time'] < window_s]
    if len(recent) == 0 and len(processes) > 0:
        return [{
            'issue': 'possible_deadlock',
            'reason': 'no activity in window',
            'time': now
        }]
    return []


def run_all_detectors(traces, processes):
    alerts = []
    alerts.extend(detect_queue_backlog(traces))
    alerts.extend(detect_pipe_latency(traces))
    alerts.extend(detect_deadlock(traces, processes))
    return alerts
