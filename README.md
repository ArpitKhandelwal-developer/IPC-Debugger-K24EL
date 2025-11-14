# Inter-Process Communication (IPC) Debugger  
### Major Project — K24EL  
A debugging and visualization tool for Pipes, Message Queues, and Shared Memory using Python.

---

## Project Overview

Inter-Process Communication (IPC) is essential in operating systems for enabling processes to exchange data and synchronize tasks. Debugging IPC is complex due to concurrency, timing dependencies, data races, and deadlocks.

The **IPC Debugger** is a GUI-based tool that allows users to simulate IPC mechanisms, visualize real-time throughput, detect synchronization issues, and export log data. It is designed to support students, developers, and researchers in understanding how IPC works internally.

---

## Team Members
- **Team Leader:** Deepansh Tank (12503753)  
- **Team Member:** Arpit Khandelwal (12503747)  
- **Section:** K24EL

---

## Features

### ✔ IPC Simulation
- Pipes (send/receive)
- Message Queues (producer/consumer)
- Shared Memory (read/write)

### ✔ Real-Time Throughput Graph
- Live updating Matplotlib graph  
- Auto-scaling y-axis  
- Shows messages per second

### ✔ Analyzer — Detects Issues
- Deadlocks  
- Backlogs  
- Slow processing  
- Latency spikes  

### ✔ PyQt5 GUI Tools
- Select IPC type  
- Set rate, delay, and process count  
- Start/Stop individual processes  
- View active processes  
- Export trace logs (JSON)

### ✔ Event Logging
Each IPC event includes:
- Timestamp  
- Type of operation  
- Payload  
- Latency details  
- Process label  

---

## System Architecture

GUI (PyQt5)
│
▼
IPC Simulator Engine
(Pipes, Queues, SHM)
│
▼
Analyzer Module
(Deadlock, Latency, Backlog)
│
▼
Visualizer Module (Matplotlib)


---

## Technology Stack

| Component | Technology |
|----------|------------|
| Programming Language | Python 3 |
| GUI | PyQt5 |
| Graphs | Matplotlib |
| IPC | Python Multiprocessing |
| Data Sharing | Pipe, Queue, SharedMemory |
| Version Control | Git & GitHub |

---

## Project Structure

IPC-Debugger/
│── main.py
│── gui.py
│── ipc_simulator.py
│── analyzer.py
│── visual.py
│── utils.py
│── requirements.txt
│── README.md


---

## Installation & Setup

### 1. Install Dependencies
Run:

pip install -r requirements.txt


### 2. Start the Application
python main.py



---

## GitHub Revision Tracking

This repository includes:
- Clean commit history  
- Version-controlled changes  
- Feature implementations  
- Bug fixes and improvements  
- Proper commit messages  

---

## Testing

Tested for:
- Pipe-based communication  
- Queue producer–consumer  
- Shared memory behavior  
- Deadlock simulation  
- High message rate handling  
- GUI responsiveness under load  
- Event logging accuracy  

---

## Future Scope

- Add mutex & semaphore visualization  
- Add socket-based communication  
- Add process dependency graph  
- Add recording & replaying of IPC sessions  
- Web-based dashboard version (Flask/React)  

---

## References

- Python Multiprocessing Docs  
- PyQt5 Documentation  
- Matplotlib Official Docs  
- Galvin: Operating System Concepts  
- GeeksForGeeks IPC Tutorials  

---

## Conclusion

The **IPC Debugger** successfully demonstrates real-time simulation of Pipes, Message Queues, and Shared Memory. The tool provides valuable insights into IPC behavior, synchronization issues, and performance bottlenecks. It is ideal for OS learning, debugging, and research-based experimentation.

---
