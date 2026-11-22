"""Sample Windows CPU and memory for the HW05 backend and optional JMeter PID.

No third-party packages are required. Output is real measurements from Windows
APIs, with timestamps in the student's Asia/Ho_Chi_Minh time zone. Start this
before a run and stop with Ctrl+C or --duration. Never use it to invent missing
Task Manager screenshots or video evidence.
"""

import argparse
import csv
import ctypes
import os
import time
from ctypes import wintypes
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


if os.name != "nt":
    raise SystemExit("This script requires Windows.")


DWORD = wintypes.DWORD
SIZE_T = ctypes.c_size_t
HANDLE = wintypes.HANDLE


class FILETIME(ctypes.Structure):
    _fields_ = [("low", DWORD), ("high", DWORD)]

    def ticks(self) -> int:
        return (self.high << 32) | self.low


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", DWORD),
        ("dwMemoryLoad", DWORD),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
    _fields_ = [
        ("cb", DWORD),
        ("PageFaultCount", DWORD),
        ("PeakWorkingSetSize", SIZE_T),
        ("WorkingSetSize", SIZE_T),
        ("QuotaPeakPagedPoolUsage", SIZE_T),
        ("QuotaPagedPoolUsage", SIZE_T),
        ("QuotaPeakNonPagedPoolUsage", SIZE_T),
        ("QuotaNonPagedPoolUsage", SIZE_T),
        ("PagefileUsage", SIZE_T),
        ("PeakPagefileUsage", SIZE_T),
        ("PrivateUsage", SIZE_T),
    ]


kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
psapi = ctypes.WinDLL("psapi", use_last_error=True)
kernel32.OpenProcess.argtypes = [DWORD, wintypes.BOOL, DWORD]
kernel32.OpenProcess.restype = HANDLE
kernel32.CloseHandle.argtypes = [HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.GetProcessTimes.argtypes = [
    HANDLE,
    ctypes.POINTER(FILETIME),
    ctypes.POINTER(FILETIME),
    ctypes.POINTER(FILETIME),
    ctypes.POINTER(FILETIME),
]
kernel32.GetProcessTimes.restype = wintypes.BOOL
kernel32.GetSystemTimes.argtypes = [
    ctypes.POINTER(FILETIME),
    ctypes.POINTER(FILETIME),
    ctypes.POINTER(FILETIME),
]
kernel32.GetSystemTimes.restype = wintypes.BOOL
kernel32.GlobalMemoryStatusEx.argtypes = [ctypes.POINTER(MEMORYSTATUSEX)]
kernel32.GlobalMemoryStatusEx.restype = wintypes.BOOL
psapi.GetProcessMemoryInfo.argtypes = [HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS_EX), DWORD]
psapi.GetProcessMemoryInfo.restype = wintypes.BOOL

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MIB = 1024 * 1024


def snapshot_process(pid: int | None) -> dict:
    if pid is None:
        return {"alive": "", "cpu_ticks": None, "start_ticks": None, "rss_mib": "", "private_mib": "", "error": "not_selected"}
    handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not handle:
        return {"alive": 0, "cpu_ticks": None, "start_ticks": None, "rss_mib": "", "private_mib": "", "error": f"OpenProcess:{ctypes.get_last_error()}"}
    try:
        start, exit_time, kernel, user = FILETIME(), FILETIME(), FILETIME(), FILETIME()
        if not kernel32.GetProcessTimes(handle, ctypes.byref(start), ctypes.byref(exit_time), ctypes.byref(kernel), ctypes.byref(user)):
            raise OSError(f"GetProcessTimes:{ctypes.get_last_error()}")
        mem = PROCESS_MEMORY_COUNTERS_EX()
        mem.cb = ctypes.sizeof(mem)
        if not psapi.GetProcessMemoryInfo(handle, ctypes.byref(mem), mem.cb):
            raise OSError(f"GetProcessMemoryInfo:{ctypes.get_last_error()}")
        return {
            "alive": 1,
            "cpu_ticks": kernel.ticks() + user.ticks(),
            "start_ticks": start.ticks(),
            "rss_mib": round(mem.WorkingSetSize / MIB, 2),
            "private_mib": round(mem.PrivateUsage / MIB, 2),
            "error": "",
        }
    except OSError as exc:
        return {"alive": 0, "cpu_ticks": None, "start_ticks": None, "rss_mib": "", "private_mib": "", "error": str(exc)}
    finally:
        kernel32.CloseHandle(handle)


def snapshot_system() -> dict:
    idle, kernel, user = FILETIME(), FILETIME(), FILETIME()
    if not kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)):
        raise OSError(f"GetSystemTimes:{ctypes.get_last_error()}")
    memory = MEMORYSTATUSEX()
    memory.dwLength = ctypes.sizeof(memory)
    if not kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):
        raise OSError(f"GlobalMemoryStatusEx:{ctypes.get_last_error()}")
    return {
        "idle_ticks": idle.ticks(),
        "total_ticks": kernel.ticks() + user.ticks(),
        "total_mem_mib": round(memory.ullTotalPhys / MIB, 2),
        "used_mem_mib": round((memory.ullTotalPhys - memory.ullAvailPhys) / MIB, 2),
        "memory_load_pct": memory.dwMemoryLoad,
    }


def cpu_pct(current: dict, previous: dict | None, elapsed_seconds: float, logical_cpus: int) -> str | float:
    if not previous or current["cpu_ticks"] is None or previous["cpu_ticks"] is None or elapsed_seconds <= 0:
        return ""
    if current["start_ticks"] != previous["start_ticks"]:
        return ""
    used_seconds = max(0, current["cpu_ticks"] - previous["cpu_ticks"]) / 10_000_000
    return round(min(100.0, 100.0 * used_seconds / elapsed_seconds / logical_cpus), 2)


def system_cpu_pct(current: dict, previous: dict | None) -> str | float:
    if previous is None:
        return ""
    total = current["total_ticks"] - previous["total_ticks"]
    idle = current["idle_ticks"] - previous["idle_ticks"]
    if total <= 0:
        return ""
    return round(max(0.0, min(100.0, 100.0 * (1 - idle / total))), 2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node-pid", required=True, type=int)
    parser.add_argument("--jmeter-pid", type=int, help="Optional java.exe PID; blank fields if omitted")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--interval", type=float, default=5.0, help="Seconds between samples (default 5)")
    parser.add_argument("--duration", type=float, help="Stop after this many seconds; otherwise Ctrl+C")
    args = parser.parse_args()
    if args.node_pid <= 0 or (args.jmeter_pid is not None and args.jmeter_pid <= 0):
        parser.error("PIDs must be positive")
    if args.interval < 1 or (args.duration is not None and args.duration <= 0):
        parser.error("interval must be >=1 and duration >0")
    if args.output.exists():
        parser.error(f"output already exists: {args.output}; choose a new run filename")
    args.output.parent.mkdir(parents=True, exist_ok=True)

    columns = [
        "time_local", "elapsed_s", "system_cpu_pct", "system_used_mem_mib", "system_total_mem_mib", "system_memory_load_pct",
        "node_pid", "node_alive", "node_cpu_pct_total", "node_rss_mib", "node_private_mib", "node_pid_reused", "node_error",
        "jmeter_pid", "jmeter_alive", "jmeter_cpu_pct_total", "jmeter_rss_mib", "jmeter_private_mib", "jmeter_pid_reused", "jmeter_error",
    ]
    logical_cpus = os.cpu_count() or 1
    start_monotonic = time.monotonic()
    prev_monotonic: float | None = None
    prev_system: dict | None = None
    prev_node: dict | None = None
    prev_jmeter: dict | None = None
    node_start: int | None = None
    jmeter_start: int | None = None

    print(f"Sampling node PID {args.node_pid}, JMeter PID {args.jmeter_pid or 'not selected'} to {args.output}", flush=True)
    try:
        with args.output.open("x", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            while True:
                now = time.monotonic()
                system = snapshot_system()
                node = snapshot_process(args.node_pid)
                jmeter = snapshot_process(args.jmeter_pid)
                if node_start is None and node["start_ticks"] is not None:
                    node_start = node["start_ticks"]
                if jmeter_start is None and jmeter["start_ticks"] is not None:
                    jmeter_start = jmeter["start_ticks"]
                node_reused = int(node_start is not None and node["start_ticks"] is not None and node["start_ticks"] != node_start)
                jmeter_reused = int(jmeter_start is not None and jmeter["start_ticks"] is not None and jmeter["start_ticks"] != jmeter_start)
                delta = 0 if prev_monotonic is None else now - prev_monotonic
                writer.writerow({
                    "time_local": datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).isoformat(timespec="seconds"),
                    "elapsed_s": round(now - start_monotonic, 2),
                    "system_cpu_pct": system_cpu_pct(system, prev_system),
                    "system_used_mem_mib": system["used_mem_mib"],
                    "system_total_mem_mib": system["total_mem_mib"],
                    "system_memory_load_pct": system["memory_load_pct"],
                    "node_pid": args.node_pid,
                    "node_alive": node["alive"],
                    "node_cpu_pct_total": cpu_pct(node, prev_node, delta, logical_cpus),
                    "node_rss_mib": node["rss_mib"],
                    "node_private_mib": node["private_mib"],
                    "node_pid_reused": node_reused,
                    "node_error": node["error"],
                    "jmeter_pid": args.jmeter_pid or "",
                    "jmeter_alive": jmeter["alive"],
                    "jmeter_cpu_pct_total": cpu_pct(jmeter, prev_jmeter, delta, logical_cpus),
                    "jmeter_rss_mib": jmeter["rss_mib"],
                    "jmeter_private_mib": jmeter["private_mib"],
                    "jmeter_pid_reused": jmeter_reused,
                    "jmeter_error": jmeter["error"],
                })
                stream.flush()
                if node_reused or jmeter_reused:
                    print("PID reuse detected; stopping to avoid mixing two processes in one run.", flush=True)
                    break
                if args.duration is not None and now - start_monotonic >= args.duration:
                    break
                prev_monotonic, prev_system, prev_node, prev_jmeter = now, system, node, jmeter
                time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Stopped by user; CSV flushed.", flush=True)


if __name__ == "__main__":
    main()
