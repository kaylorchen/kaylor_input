# kaylor_input

局域网文本输入中继工具。手机打开网页，输入文本，点击 Send，文本被粘贴到电脑光标位置。自动适配 X11 和 Wayland。

## 快速启动

```bash
cd /home/kaylor/work/kaylor_input
conda activate kaylor_input
python app.py
```

- 本机访问：`http://localhost:5000`
- 手机/其他设备访问：`http://<IP>:5000`（`hostname -I` 查看 IP）

## 环境部署

### 1. 系统依赖

**X11**

```bash
sudo apt install xclip xdotool
```

**Wayland**

```bash
sudo apt install wl-clipboard ydotool
sudo usermod -a -G input $USER
# 重新登录使 input 组生效
```

> 服务自动通过 `WAYLAND_DISPLAY` / `XDG_SESSION_TYPE` 检测环境，无需手动切换。

### 2. Python 环境

仅依赖 Flask 一个库。

```bash
conda create -n kaylor_input python=3.10 -y
conda activate kaylor_input
pip install flask
```

## 使用

1. 电脑启动服务 `python app.py`
2. 手机连接同一 WiFi
3. 手机浏览器打开 `http://<电脑IP>:5000`
4. 电脑光标放在需要输入的位置
5. 手机输入文本，点 Send（或 Enter），文本粘贴到光标处

## 开机自启动（systemd）

创建服务文件：

```bash
sudo tee /etc/systemd/system/kaylor-input.service << 'EOF'
[Unit]
Description=Kaylor Input Text Relay
After=network.target

[Service]
Type=simple
ExecStart=/home/kaylor/miniconda3/envs/kaylor_input/bin/python /home/kaylor/work/kaylor_input/app.py
WorkingDirectory=/home/kaylor/work/kaylor_input
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF
```

启动并启用：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now kaylor-input
systemctl status kaylor-input
```

> `ExecStart` 中的 conda 路径按实际情况调整：`conda info --envs` 查看环境所在路径。

## 工作原理

| | X11 | Wayland |
|---|---|---|
| 设置文本 | `xclip -selection primary` | `wl-copy` + `wl-copy --primary` |
| 粘贴 | `xdotool click 2`（中键粘贴） | `ydotool click 3` |
| 选区恢复 | 保存并恢复原有 PRIMARY | — |

两种方案都不依赖键盘快捷键，通过鼠标点击触发粘贴，全应用通用。
