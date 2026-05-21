import os
import subprocess
import tempfile
import time
from flask import Flask, request, jsonify, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))


TERMINAL_KEYWORDS = ("terminal", "term", "xterm", "konsole", "alacritty",
                     "kitty", "tilix", "st-", "rxvt", "foot", "Terminal", "Term")


def _is_macos():
    return os.uname().sysname == "Darwin"


def _is_wayland():
    return bool(os.environ.get("WAYLAND_DISPLAY")) or os.environ.get("XDG_SESSION_TYPE") == "wayland"


def _is_terminal_x11():
    try:
        wid = subprocess.run(
            ["xdotool", "getactivewindow"],
            capture_output=True, text=True, timeout=2,
        )
        if wid.returncode != 0:
            return False
        wmclass = subprocess.run(
            ["xprop", "-id", wid.stdout.strip(), "WM_CLASS"],
            capture_output=True, text=True, timeout=2,
        )
        return any(kw in wmclass.stdout for kw in TERMINAL_KEYWORDS)
    except Exception:
        return False


def type_text(text):
    if _is_macos():
        _type_darwin(text)
    elif _is_wayland():
        _type_wayland(text)
    else:
        _type_x11(text)


def _type_darwin(text):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(text)
        tmp_path = f.name
    try:
        with open(tmp_path) as fh:
            subprocess.run(
                ["pbcopy"], stdin=fh,
                check=True, timeout=5,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
    finally:
        os.unlink(tmp_path)

    time.sleep(0.05)
    subprocess.run(
        ["osascript", "-e",
         'tell application "System Events" to keystroke "v" using command down'],
        check=True, timeout=5,
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def _type_x11(text):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(text)
        tmp_path = f.name
    try:
        with open(tmp_path) as fh:
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                stdin=fh, check=True, timeout=5,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        with open(tmp_path) as fh:
            subprocess.run(
                ["xclip", "-selection", "primary"],
                stdin=fh, check=True, timeout=5,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
    finally:
        os.unlink(tmp_path)

    time.sleep(0.05)
    keys = "ctrl+shift+v" if _is_terminal_x11() else "ctrl+v"
    subprocess.run(
        ["xdotool", "key", keys],
        check=True, timeout=5,
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def _type_wayland(text):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(text)
        tmp_path = f.name
    try:
        with open(tmp_path) as fh:
            subprocess.run(
                ["wl-copy"], stdin=fh,
                check=True, timeout=5,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        with open(tmp_path) as fh:
            subprocess.run(
                ["wl-copy", "--primary"], stdin=fh,
                check=True, timeout=5,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
    finally:
        os.unlink(tmp_path)
    time.sleep(0.15)
    subprocess.run(
        ["ydotool", "key", "ctrl+v"],
        check=True, timeout=5,
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/send", methods=["POST"])
def send_text():
    data = request.get_json(silent=True)
    if not data or not isinstance(data.get("text"), str):
        return jsonify({"error": "Missing 'text' field"}), 400

    text = data["text"].strip()
    if not text:
        return jsonify({"error": "Text is empty"}), 400

    try:
        type_text(text)
        return jsonify({"ok": True, "text": text})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Input timed out"}), 500
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Input tool error: {e}"}), 500
    except FileNotFoundError as e:
        if _is_macos():
            hint = "macOS pbcopy/osascript unavailable (should be built-in)"
        elif _is_wayland():
            hint = "Wayland: apt install wl-clipboard ydotool && usermod -a -G input $USER (re-login) && ydotoold &"
        else:
            hint = "X11: apt install xclip xdotool"
        return jsonify({"error": f"Tool not found: {e}. {hint}"}), 500


if __name__ == "__main__":
    if _is_wayland() and not _is_macos():
        try:
            subprocess.run(["pgrep", "ydotoold"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            subprocess.Popen(
                ["ydotoold"],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=False)
