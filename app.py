import os
import subprocess
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
    # Save current PRIMARY selection
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

    # Set PRIMARY selection to our text
    subprocess.run(
        ["xclip", "-selection", "primary"],
        input=text, text=True, check=True, timeout=5,
    )

    # Middle-click to paste (universal X11 paste)
    time.sleep(0.05)
    subprocess.run(["xdotool", "click", "2"], check=True, timeout=5)

    # Restore original PRIMARY selection
    time.sleep(0.1)
    if has_saved:
        subprocess.run(
            ["xclip", "-selection", "primary"],
            input=saved_text, text=True, timeout=5,
        )


def _type_wayland(text):
    subprocess.run(["wl-copy"], input=text, text=True, check=True, timeout=5)
    subprocess.run(["wl-copy", "--primary"], input=text, text=True, check=True, timeout=5)
    time.sleep(0.15)
    subprocess.run(["ydotool", "click", "3"], check=True, timeout=5)


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
            subprocess.Popen(["ydotoold"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    app.run(host="0.0.0.0", port=5000, debug=False)
