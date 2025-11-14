# ipc_simulator.py
import multiprocessing as mp
import time
import uuid
from multiprocessing import shared_memory
from multiprocessing.managers import SyncManager
from utils import trace_event


class IPCSimulator:
    def __init__(self):
        self.manager = SyncManager()
        self.manager.start()
        self.processes = {}
        self.traces = self.manager.list()
        self.running = mp.Event()

    def create_pipe(self):
        return mp.Pipe(duplex=True)

    def create_queue(self):
        return self.manager.Queue()

    def create_shared_memory(self, name=None, size=1024):
        if name is None:
            name = f'ipcshm_{uuid.uuid4().hex[:8]}'
        shm = shared_memory.SharedMemory(create=True, size=size, name=name)
        return name, shm

    def start_process(self, pid, target, args=()):
        p = mp.Process(target=target, args=args, name=str(pid))
        p.start()
        self.processes[pid] = p
        trace_event(self.traces, 'process_start', pid)
        return p

    def stop_process(self, pid):
        p = self.processes.get(pid)
        if p and p.is_alive():
            p.terminate()
            p.join(timeout=1)
            trace_event(self.traces, 'process_stop', pid)

    def shutdown(self):
        for pid in list(self.processes):
            try:
                self.stop_process(pid)
            except Exception:
                pass
        self.manager.shutdown()


# -------- Worker functions --------

# -------- Worker functions (updated with error handling) --------

def pipe_sender(conn, label, rate_ms=100, msg_prefix='msg'):
    i = 0
    try:
        while True:
            payload = f'{msg_prefix}-{i}'
            ts = time.time()
            try:
                conn.send((payload, ts))
            except (BrokenPipeError, EOFError):
                break  # Exit cleanly if pipe closed
            i += 1
            time.sleep(rate_ms / 1000)
    except KeyboardInterrupt:
        return
    finally:
        conn.close()


def pipe_receiver(conn, label, traces, processing_ms=0):
    try:
        while True:
            if conn.poll(0.2):
                try:
                    payload, ts = conn.recv()
                except (EOFError, BrokenPipeError):
                    break  # Exit if pipe closed
                rcv_ts = time.time()
                trace_event(traces, 'pipe_message', label, {
                    'payload': payload,
                    'sent_ts': ts,
                    'rcv_ts': rcv_ts
                })
                if processing_ms:
                    time.sleep(processing_ms / 1000)
    except KeyboardInterrupt:
        return
    finally:
        conn.close()


def queue_sender(q, traces, label, rate_ms=100, msg_prefix='qmsg'):
    i = 0
    try:
        while True:
            payload = f'{msg_prefix}-{i}'
            ts = time.time()
            try:
                q.put((payload, ts))
            except Exception:
                break  # Manager queue closed
            trace_event(traces, 'queue_put', label, {'payload': payload, 'ts': ts})
            i += 1
            time.sleep(rate_ms / 1000)
    except KeyboardInterrupt:
        return


def queue_receiver(q, traces, label, processing_ms=0):
    try:
        while True:
            try:
                item = q.get(timeout=1)
            except Exception:
                break  # Manager queue closed
            payload, ts = item
            rcv_ts = time.time()
            trace_event(traces, 'queue_get', label, {'payload': payload, 'sent_ts': ts, 'rcv_ts': rcv_ts})
            if processing_ms:
                time.sleep(processing_ms / 1000)
    except KeyboardInterrupt:
        return


def shm_worker(name, size, traces, label, role='reader', interval_ms=200, write_payload=b''):
    try:
        shm = shared_memory.SharedMemory(name=name)
        i = 0
        while True:
            if role == 'writer':
                payload = (write_payload or f'shm-{i}'.encode())[:size]
                shm.buf[:len(payload)] = payload
                trace_event(traces, 'shm_write', label, {'payload': payload.decode(errors='ignore')})
                i += 1
            else:
                snapshot = bytes(shm.buf[:size]).rstrip(b"\x00")
                trace_event(traces, 'shm_read', label, {'payload': snapshot.decode(errors='ignore')})
            time.sleep(interval_ms / 1000)
    except Exception as e:
        trace_event(traces, 'shm_error', label, {'error': str(e)})
    finally:
        try:
            shm.close()
        except Exception:
            pass
