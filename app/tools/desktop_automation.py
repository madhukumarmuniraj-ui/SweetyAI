import os
import subprocess
import platform
import psutil

def open_application(app_name: str) -> str:
    """Safely opens a recognized desktop application on Windows."""
    app_lower = app_name.lower().strip()
    safe_apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "explorer": "explorer.exe",
        "cmd": "cmd.exe",
        "terminal": "wt.exe",
        "code": "code",
        "vscode": "code",
        "edge": "msedge.exe",
        "chrome": "chrome.exe"
    }

    executable = safe_apps.get(app_lower)
    if not executable:
        return f"Application '{app_name}' is not in the safe whitelist of launchable applications."

    try:
        if platform.system() == "Windows":
            subprocess.Popen([executable], shell=True)
            return f"Launched {app_name} successfully."
        else:
            return f"Opening applications is currently only supported on Windows."
    except Exception as e:
        return f"Failed to launch {app_name}: {str(e)}"

def get_system_info() -> str:
    """Returns real-time system metrics (CPU usage, Memory utilization, OS details)."""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        info = (
            f"System Information:\n"
            f"- OS: {platform.system()} {platform.release()} ({platform.machine()})\n"
            f"- CPU Usage: {cpu_percent}%\n"
            f"- RAM Usage: {mem.percent}% ({mem.used // (1024**2)} MB / {mem.total // (1024**2)} MB)\n"
            f"- Disk Usage: {disk.percent}% ({disk.free // (1024**3)} GB free)"
        )
        return info
    except Exception as e:
        return f"Failed to retrieve system info: {str(e)}"
