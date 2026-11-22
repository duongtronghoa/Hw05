# Resource monitoring during HW05 runs

`scripts/monitor_resources.py` writes a real timestamped CSV using Windows APIs. It does not require `psutil` and does **not** replace the required screenshot or Vietnamese narrated video showing JMeter/CLI and Task Manager in the same frame.

Start the backend first. Obtain its PID from the process listening on port 3000:

```powershell
(Get-NetTCPConnection -LocalPort 3000 -State Listen).OwningProcess
```

From `hw05-work/`, run the monitor in a separate PowerShell window before a performance run. Replace `<NODE_PID>`, duration and output name. Allow a little longer than the JMeter run; use Ctrl+C to end sooner.

```powershell
python .\scripts\monitor_resources.py --node-pid <NODE_PID> --interval 5 --duration 600 --output .\results\load\resources.csv
```

Optionally provide `--jmeter-pid <JAVA_PID>` if JMeter's Java process is already running. Find it with `Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'java.exe' -and $_.CommandLine -match 'ApacheJMeter' } | Select-Object ProcessId,CommandLine`. The logger does not auto-select among multiple Java processes. If no Java PID is supplied, JMeter process fields are intentionally blank; system CPU/RAM still reflect the whole computer.

Use a different CSV filename for every run. The script refuses to overwrite existing evidence. Columns ending `_mib` are mebibytes (MiB); process CPU percent is normalized to the whole machine, where 100% means all logical CPUs. The first CPU sample is blank because there is no previous point. The `node_alive`, `*_error` and `*_pid_reused` fields show whether a process disappeared, could not be read, or restarted; do not treat missing CPU values as zero. `node_rss_mib` is the working set, while `node_private_mib` is private committed memory. Timestamps use `Asia/Ho_Chi_Minh` (+07:00).

Keep the CSV with the corresponding raw `.jtl`, `jmeter.log`, HTML dashboard, and a run manifest showing the backend PID and exact test interval. Take the required Task Manager screenshot while the load is running and record the video with your own Vietnamese voice. If the backend is restarted, EShop resets its database and the synthetic admin accounts must be prepared again.
