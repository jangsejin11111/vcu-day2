"""Double-click launcher for the local workshop. No external Python packages."""
import ctypes, json, os, shutil, subprocess, sys, time, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SITE = "http://localhost:5174"
MODEL = "qwen3:4b-instruct"

def fetch(url, data=None):
    req = urllib.request.Request(url, None if data is None else json.dumps(data).encode(), {"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=3) as response:
        return json.load(response)

def probe(url):
    try: return fetch(url)
    except Exception: return None

def wait(url):
    deadline = time.monotonic() + 40
    while time.monotonic() < deadline:
        value = probe(url)
        if value is not None: return value
        time.sleep(.7)
    raise RuntimeError("Service did not start: " + url + ". Check .data/launcher logs.")

def start(exe, args, name, env):
    stamp = str(time.time_ns())
    with (ROOT / ".data" / ("launcher-"+name+"-"+stamp+"-out.log")).open("ab") as out, (ROOT / ".data" / ("launcher-"+name+"-"+stamp+"-error.log")).open("ab") as err:
        return subprocess.Popen([str(exe), *args], cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err, creationflags=subprocess.CREATE_NO_WINDOW)

def worker_running():
    command = "Get-CimInstance Win32_Process -Filter \"Name = 'python.exe' OR Name = 'pythonw.exe'\" | Where-Object { $_.CommandLine -match 'scripts[\\/]vad_worker\\.py' -and $_.CommandLine -match '--site\\s+http://localhost:5174(?:\\s|$)' } | Select-Object -ExpandProperty ProcessId"
    result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", command], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=20)
    if result.returncode: raise RuntimeError("Could not check running workers: " + result.stderr)
    return bool(result.stdout.strip())

def main():
    # A Windows mutex prevents two double-clicks from launching duplicate services.
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateMutexW.restype = ctypes.c_void_p
    kernel.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p]
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel.CreateMutexW(None, False, "Local\\KArtsVCUWorkshop02Launcher")
    if not handle: raise ctypes.WinError(ctypes.get_last_error())
    if ctypes.get_last_error() == 183:
        kernel.CloseHandle(handle)
        print("Workshop is already starting.")
        return
    try:
        (ROOT / ".data").mkdir(exist_ok=True)
        env = os.environ.copy()
        for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
            key, sep, value = line.partition("=")
            if sep and key in ("VCU_ADMIN_PASSWORD", "VCU_AUTH_SECRET"): env[key] = value.strip()
        if not env.get("VCU_ADMIN_PASSWORD"): raise RuntimeError("Set VCU_ADMIN_PASSWORD in .env first.")
        print("[1/3] Website", flush=True)
        state = probe(SITE + "/api/state")
        if state is None:
            node = shutil.which("node")
            if not node: raise RuntimeError("Node.js is not installed.")
            start(node, ["server/dev.mjs"], "web", env)
            state = wait(SITE + "/api/state")
        if "comments" not in state: raise RuntimeError("Port 5174 belongs to a different service.")
        fetch(SITE + "/api/login", {"password":env["VCU_ADMIN_PASSWORD"]})
        print("[2/3] Ollama", flush=True)
        tags = probe("http://127.0.0.1:11434/api/tags")
        if tags is None:
            candidates = [ROOT.parent / ".local-ai/ollama/ollama.exe", Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Ollama/ollama.exe"]
            ollama = next((p for p in candidates if p.is_file()), None) or shutil.which("ollama")
            if not ollama: raise RuntimeError("Ollama was not found.")
            env.update(OLLAMA_HOST="127.0.0.1:11434", OLLAMA_NO_CLOUD="1")
            start(ollama, ["serve"], "ollama", env)
            tags = wait("http://127.0.0.1:11434/api/tags")
        if MODEL not in [m["name"] for m in tags.get("models", [])]:
            raise RuntimeError("Download the model once: ollama pull " + MODEL)
        print("[3/3] Analysis worker", flush=True)
        if not worker_running():
            worker = start(sys.executable, ["-u", "scripts/vad_worker.py", "--site", SITE], "worker", env)
            time.sleep(2)
            if worker.poll() is not None: raise RuntimeError("Worker stopped. Check .data/launcher-worker logs.")
            print("Worker started:", worker.pid)
        else: print("Worker already running.")
        if "--no-browser" not in sys.argv: os.startfile(SITE + "/#board")
        print("Ready. All services remain running in the background.")
    finally: kernel.CloseHandle(handle)

if __name__ == "__main__":
    try: main()
    except Exception as error:
        print("ERROR:", error)
        sys.exit(1)
