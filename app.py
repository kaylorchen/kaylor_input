import os
import subprocess
import tempfile
import time
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="static")


def _is_wayland():
    return bool(os.environ.get("WAYLAND_DISPLAY")) or os.environ.get("XDG_SESSION_TYPE") == "wayland"


def type_text(text):
    if _is_wayland():
        _type_wayland(text)
    else:
        _type_x11(text)


def _type_x11(text):
    try:
        saved = subprocess.run(
            ["xclip", "-selection", "primary", "-o"],
            capture_output=True, text=True, timeout=2,
        )
        has_saved = saved.returncode == 0
        saved_text = saved.stdout if has_saved else ""
    except Exception:
        has_saved = False
        saved_text = ""

    subprocess.run(
        ["xclip", "-selection", "primary"],
        input=text, text=True, check=True, timeout=5,
    )

    time.sleep(0.05)
    subprocess.run(
        ["xdotool", "click", "2"],
        check=True, timeout=5,
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    time.sleep(0.1)
    if has_saved:
        subprocess.run(
            ["xclip", "-selection", "primary"],
            input=saved_text, text=True, timeout=5,
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
        ["ydotool", "click", "3"],
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
        if e.returncode == -13:  # SIGPIPE: click sent, pipe closed on exit
            return jsonify({"ok": True, "text": text})
        return jsonify({"error": f"Input tool error: {e}"}), 500
    except FileNotFoundError as e:
        if _is_wayland():
            hint = "Wayland: apt install wl-clipboard ydotool && usermod -a -G input $USER (re-login) && ydotoold &"
        else:
            hint = "X11: apt install xclip xdotool"
        return jsonify({"error": f"Tool not found: {e}. {hint}"}), 500


if __name__ == "__main__":
    if _is_wayland():
        try:
            subprocess.run(["pgrep", "ydotoold"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            subprocess.Popen(
                ["ydotoold"],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=False)
