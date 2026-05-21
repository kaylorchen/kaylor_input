# kaylor_input

局域网文本输入中继工具。手机打开网页，输入文本，点击 Send，文本被粘贴到电脑光标位置。自动适配 X11、Wayland 和 macOS。

## 安装 & 启用

### Linux (Debian/Ubuntu)

```bash
sudo apt install dpkg-dev debhelper
dpkg-buildpackage -us -uc -b
sudo dpkg -i ../kaylor-input_1.0.0_all.deb
sudo apt install -f          # 补全依赖
systemctl --user enable --now kaylor-input
sudo loginctl enable-linger $USER   # 开机自启
```

### macOS

```bash
# 安装
sudo mkdir -p /usr/local/lib/kaylor-input
sudo cp app.py static/index.html /usr/local/lib/kaylor-input/
pip3 install flask

# 服务
cp com.kaylor.input.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.kaylor.input.plist
```

> macOS 需要授予辅助功能权限：系统设置 → 隐私与安全性 → 辅助功能 → 添加终端（或 iTerm）。

- 本机访问：`http://localhost:5000`
- 手机/其他设备访问：`http://<IP>:5000`

## 依赖

| 平台 | 工具 | 安装方式 |
|---|---|---|
| Linux | `python3-flask` | `apt install python3-flask` |
| Linux (X11) | `xdotool xclip` | `apt install xdotool xclip` |
| Linux (Wayland) | `wl-clipboard ydotool` | `apt install wl-clipboard ydotool` |
| macOS | `python3` `flask` | 系统自带 `pbcopy` + `osascript`，无需额外依赖 |

## 工作原理

| | X11 | Wayland | macOS |
|---|---|---|---|
| 设置文本 | `xclip` | `wl-copy` | `pbcopy` |
| 粘贴 | `xdotool key ctrl+v` | `ydotool key ctrl+v` | `osascript Cmd+V` |
| 终端适配 | 自动检测 WM_CLASS → `Ctrl+Shift+V` | — | 不需要（`Cmd+V` 通用） |
