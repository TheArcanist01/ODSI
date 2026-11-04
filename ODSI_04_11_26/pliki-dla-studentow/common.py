import base64
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "konfiguracja" / "dostep.conf"
SERVER_URL = "http://127.0.0.1:8080"


def read_blocks():
    text = CONFIG_PATH.read_text(encoding="utf-8")
    return [block.strip() + "\n" for block in text.split("\n\n") if block.strip()]


FULL_CONFIG = CONFIG_PATH.read_text(encoding="utf-8")
BLOCKS = read_blocks()
STAGE_DIRECTORIES = "\n".join(BLOCKS[:2])
STAGE_PANEL = "\n".join(BLOCKS[:3])
STAGE_CGI = "\n".join(BLOCKS[:4])


def compose(*args, interactive=False):
    command = ["docker", "compose", *args]
    if interactive:
        return subprocess.run(command, cwd=BASE_DIR).returncode
    result = subprocess.run(command, cwd=BASE_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return result.stdout + result.stderr


def wait_for_server(timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(SERVER_URL + "/", timeout=2).close()
            return
        except OSError:
            time.sleep(0.5)
    raise SystemExit("Server did not start: " + compose("logs", "--tail", "30", "web"))


def apply_config(text):
    CONFIG_PATH.write_bytes(text.encode("utf-8"))
    check = compose("exec", "-T", "web", "httpd", "-t")
    if "Syntax OK" not in check:
        CONFIG_PATH.write_bytes(FULL_CONFIG.encode("utf-8"))
        raise SystemExit(check)
    compose("restart", "web")
    wait_for_server()


def start_server():
    compose("up", "-d", "--build", "web")
    wait_for_server()


def restore_config():
    CONFIG_PATH.write_bytes(FULL_CONFIG.encode("utf-8"))


def request(path, credentials=None):
    http_request = urllib.request.Request(SERVER_URL + path)
    if credentials:
        token = base64.b64encode(":".join(credentials).encode("utf-8")).decode("ascii")
        http_request.add_header("Authorization", "Basic " + token)
    try:
        with urllib.request.urlopen(http_request, timeout=5) as response:
            return response.status, response.headers, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, error.headers, error.read().decode("utf-8", "replace")


def log_lines(pattern):
    return [line for line in compose("logs", "--tail", "30", "web").splitlines() if pattern in line]
