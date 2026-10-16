import os
import subprocess
import glob

def list_directory(path: str = ".") -> str:
    """List files and directories in the given path safely."""
    try:
        items = os.listdir(path)
        return f"Contents of {path}:\n" + "\n".join([f"  - {item}" for item in sorted(items)])
    except Exception as e:
        return f"Error listing directory: {str(e)}"

def run_system_command(command: str) -> str:
    """Run a safe local terminal command and return the output."""
    # Restrict dangerous root commands for safety
    forbidden = ["rm -rf /", "mkfs", ":(){ :|:& };:"]
    if any(f in command for f in forbidden):
        return "Command blocked by security policy."
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout if result.returncode == 0 else result.stderr
        return f"Exit Code: {result.returncode}\nOutput:\n{output.strip()}"
    except Exception as e:
        return f"Execution error: {str(e)}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(run_system_command(" ".join(sys.argv[1:])))
