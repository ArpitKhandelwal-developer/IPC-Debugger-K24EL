# gui.py
# TODO: Improve GUI responsiveness for high throughput

import sys
import time
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget,
    QHBoxLayout, QFormLayout, QSpinBox, QComboBox,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import QTimer
from visual import MiniPlot
from ipc_simulator import IPCSimulator, pipe_sender, pipe_receiver, queue_sender, queue_receiver, shm_worker
from analyzer import run_all_detectors


class IPCDebuggerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IPC Debugger — College Project")
        self.setGeometry(200, 200, 1000, 600)

        self.sim = IPCSimulator()
        self.process_id_counter = 1
        self.active_items = []

        # Call the function to build the GUI
        self._build_ui()

        # Timer to refresh metrics and alerts
        self.timer = QTimer()
        self.timer.timeout.connect(self._periodic_update)
        self.timer.start(800)

        # For plotting throughput
        self.plot_x = list(range(30))
        self.plot_y = [0] * 30

    # --------------------------------------------
    # UI Builder
    # --------------------------------------------
    def _build_ui(self):
        main = QHBoxLayout()

        # Left panel - controls
        left = QVBoxLayout()
        left.setSpacing(10)
        cfg = QFormLayout()

        self.ipc_type = QComboBox()
        self.ipc_type.addItems(["pipe", "queue", "shared_memory"])
        cfg.addRow("IPC Type:", self.ipc_type)

        self.rate_spin = QSpinBox()
        self.rate_spin.setRange(10, 5000)
        self.rate_spin.setValue(200)
        cfg.addRow("Send rate (ms):", self.rate_spin)

        self.proc_count = QSpinBox()
        self.proc_count.setRange(1, 10)
        self.proc_count.setValue(2)
        cfg.addRow("Processes:", self.proc_count)

        self.proc_processing = QSpinBox()
        self.proc_processing.setRange(0, 2000)
        self.proc_processing.setValue(0)
        cfg.addRow("Processing delay (ms):", self.proc_processing)

        add_btn = QPushButton("Start Simulation")
        add_btn.clicked.connect(self.start_simulation)
        cfg.addRow(add_btn)

        left.addLayout(cfg)

        self.process_list = QListWidget()
        left.addWidget(QLabel("Active Processes:"))
        left.addWidget(self.process_list)

        stop_btn = QPushButton("Stop Selected Process")
        stop_btn.clicked.connect(self.stop_selected_process)
        left.addWidget(stop_btn)

        export_btn = QPushButton("Export Trace (JSON)")
        export_btn.clicked.connect(self.export_traces)
        left.addWidget(export_btn)

        main.addLayout(left, 2)

        # Right panel - graph and alerts
        right = QVBoxLayout()
        right.addWidget(QLabel("Throughput (messages / second)"))
        self.plot = MiniPlot()
        right.addWidget(self.plot)

        right.addWidget(QLabel("Detectors & Alerts"))
        self.alerts_list = QListWidget()
        right.addWidget(self.alerts_list)

        main.addLayout(right, 3)

        self.setLayout(main)

    # --------------------------------------------
    # Simulation Start
    # --------------------------------------------
    def start_simulation(self):
        ipc = self.ipc_type.currentText()
        count = self.proc_count.value()
        rate = self.rate_spin.value()
        processing = self.proc_processing.value()

        if ipc == "pipe":
            for i in range(count):
                parent_conn, child_conn = self.sim.create_pipe()
                pid_sender = f"pipe_sender_{self.process_id_counter}"
                pid_receiver = f"pipe_receiver_{self.process_id_counter}"
                self.sim.start_process(pid_sender, pipe_sender, args=(parent_conn, pid_sender, rate, f"p{i}"))
                self.sim.start_process(pid_receiver, pipe_receiver, args=(child_conn, pid_receiver, self.sim.traces, processing))
                self.process_list.addItem(pid_sender)
                self.process_list.addItem(pid_receiver)
                self.active_items.extend([pid_sender, pid_receiver])
                self.process_id_counter += 1

        elif ipc == "queue":
            q = self.sim.create_queue()
            for i in range(count):
                pid_s = f"queue_sender_{self.process_id_counter}"
                pid_r = f"queue_receiver_{self.process_id_counter}"
                self.sim.start_process(pid_s, queue_sender, args=(q, self.sim.traces, pid_s, rate, f"q{i}"))
                self.sim.start_process(pid_r, queue_receiver, args=(q, self.sim.traces, pid_r, processing))
                self.process_list.addItem(pid_s)
                self.process_list.addItem(pid_r)
                self.active_items.extend([pid_s, pid_r])
                self.process_id_counter += 1

        else:
            name, shm = self.sim.create_shared_memory(size=256)
            pid_writer = f"shm_writer_{self.process_id_counter}"
            self.sim.start_process(pid_writer, shm_worker, args=(name, 256, self.sim.traces, pid_writer, "writer", 200, b"hello"))
            self.process_list.addItem(pid_writer)
            self.active_items.append(pid_writer)

            for i in range(max(1, count - 1)):
                pid_r = f"shm_reader_{self.process_id_counter}_{i}"
                self.sim.start_process(pid_r, shm_worker, args=(name, 256, self.sim.traces, pid_r, "reader", 300, b""))
                self.process_list.addItem(pid_r)
                self.active_items.append(pid_r)
            self.process_id_counter += 1

    # --------------------------------------------
    # Periodic GUI Update
    # --------------------------------------------
    def _periodic_update(self):
        now = time.time()
        window = 5.0
        recent = [t for t in list(self.sim.traces) if now - t["time"] < window]
        msgs = sum(1 for t in recent if t["type"] in ("pipe_message", "queue_get", "queue_put", "shm_write", "shm_read"))
        per_sec = msgs / window
        self.plot_y.append(per_sec)
        self.plot_y.pop(0)
        self.plot.refresh_plot(self.plot_x, self.plot_y)


        alerts = run_all_detectors(self.sim.traces, self.sim.processes)
        self.setWindowTitle(f"IPC Debugger — Running Processes: {len(self.active_items)}")

        self.alerts_list.clear()
        for a in alerts:
            self.alerts_list.addItem(json.dumps(a))

    # --------------------------------------------
    # Stop Process
    # --------------------------------------------
    def stop_selected_process(self):
        sel = self.process_list.currentItem()
        if not sel:
            QMessageBox.warning(self, "No selection", "Please select a process to stop.")
            return
        pid = sel.text()
        self.sim.stop_process(pid)
        self.process_list.takeItem(self.process_list.row(sel))
        if pid in self.active_items:
            self.active_items.remove(pid)

    # --------------------------------------------
    # Export Traces
    # --------------------------------------------
    def export_traces(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save traces", filter="JSON (*.json)")
        if not path:
            return
        with open(path, "w") as f:
            json.dump(list(self.sim.traces), f, indent=2)
        QMessageBox.information(self, "Exported", "Traces exported successfully")
