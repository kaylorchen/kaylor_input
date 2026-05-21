import os
import subprocess
import time
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="static")


def type_via_primary_selection(text):
    """Paste text via X11 PRIMARY selection + middle-click. Works everywhere."""
    if os.environ.get("WAYLAND_DISPLAY"):
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
    # wl-copy sets clipboard, ydotool simulates Ctrl+V
    # ydotool requires input group membership: sudo usermod -a -G input $USER
    subprocess.run(["wl-copy"], input=text, text=True, check=True, timeout=5)
    time.sleep(0.05)
    subprocess.run(
        ["ydotool", "key", "29:1", "47:1", "47:0", "29:0"],
        check=True, timeout=5,
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
        type_via_primary_selection(text)
        return jsonify({"ok": True, "text": text})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Input timed out"}), 500
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Input tool error: {e}"}), 500
    except FileNotFoundError as e:
        is_wayland = bool(os.environ.get("WAYLAND_DISPLAY"))
        if is_wayland:
            hint = "Wayland requires: sudo apt install wl-clipboard ydotool && sudo usermod -a -G input $USER (re-login needed)"
        else:
            hint = "X11 requires: sudo apt install xclip xdotool"
        return jsonify({"error": f"Tool not found: {e}. {hint}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
