"""Run real Plasma components on an isolated software-rendered Wayland compositor."""
import ast
import json
import os
from pathlib import Path
import subprocess
import time

from PIL import Image

assert os.getuid() != 0, "Run the desktop as an unprivileged user"

artifacts = Path("/tmp/plasma-artifacts")
runtime = Path("/tmp/plasma-runtime")
runtime.mkdir(mode=0o700)
os.environ.update(
    DISPLAY=":99",
    XDG_RUNTIME_DIR=str(runtime),
    WAYLAND_DISPLAY="wayland-smoke",
    XDG_SESSION_TYPE="wayland",
    XDG_CURRENT_DESKTOP="KDE",
    KDE_FULL_SESSION="true",
    KDE_SESSION_VERSION="6",
    QT_QPA_PLATFORM="wayland",
    LIBGL_ALWAYS_SOFTWARE="1",
    GALLIUM_DRIVER="llvmpipe",
)
processes = []
logs = []


def start(name, command):
    log = (artifacts / f"{name}.log").open("w")
    logs.append(log)
    processes.append(subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT))


def wait_for(check, description):
    deadline = time.monotonic() + 60
    last_error = ""
    while time.monotonic() < deadline:
        if any(process.poll() is not None for process in processes):
            raise RuntimeError(f"A desktop process exited while waiting for {description}")
        try:
            if check():
                return
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError, SyntaxError) as error:
            last_error = f"{error}: {getattr(error, 'output', '')}"
        time.sleep(1)
    raise TimeoutError(f"{description}: {last_error}")


def dbus(destination, path, method, *arguments):
    return subprocess.check_output(
        ["gdbus", "call", "--session", "--dest", destination, "--object-path", path,
         "--method", method, *arguments], text=True, stderr=subprocess.STDOUT, timeout=5,
    )


layout = {}


def shell_ready():
    output = dbus("org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript",
                  "print(JSON.stringify({desktops: desktops().length, panels: panels().length}))")
    layout.update(json.loads(ast.literal_eval(output)[0]))
    return layout.get("desktops", 0) > 0 and layout.get("panels", 0) > 0


def rendered():
    subprocess.run(["import", "-display", ":99", "-window", "root",
                    str(artifacts / "plasma.png")], check=True, timeout=10)
    with Image.open(artifacts / "plasma.png") as screenshot:
        assert screenshot.size == (1280, 800)
        colors = screenshot.convert("RGB").getcolors(maxcolors=20)
        return colors is None


try:
    start("xvfb", ["Xvfb", ":99", "-screen", "0", "1280x800x24", "-nolisten", "tcp"])
    wait_for(lambda: Path("/tmp/.X11-unix/X99").is_socket(), "Xvfb socket")
    start("kwin", ["kwin_wayland", "--x11-display", ":99", "--socket", "wayland-smoke",
                   "--width", "1280", "--height", "800", "--no-lockscreen"])
    wait_for(lambda: (runtime / "wayland-smoke").is_socket(), "KWin Wayland socket")
    start("plasmashell", ["plasmashell"])
    wait_for(shell_ready, "Plasma desktop and panel")
    support = dbus("org.kde.KWin", "/KWin", "org.kde.KWin.supportInformation")
    (artifacts / "kwin-support.txt").write_text(ast.literal_eval(support)[0])
    assert "llvmpipe" in support.lower(), "Expected Mesa software rendering"
    wait_for(rendered, "non-blank rendered desktop")
    assert all(process.poll() is None for process in processes)
    (artifacts / "result.json").write_text(json.dumps({
        "status": "passed", "uid": os.getuid(), "renderer": "llvmpipe",
        "layout": layout, "scope": "KWin Wayland and Plasma shell startup, not a login session",
    }, indent=2) + "\n")
    print("Plasma Wayland smoke test passed:", layout, flush=True)
finally:
    for process in reversed(processes):
        if process.poll() is None:
            process.terminate()
    for process in processes:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
    for log in logs:
        log.close()
