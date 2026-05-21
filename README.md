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

## 系统依赖

### X11

```bash
sudo apt install xclip xdotool
```

### Wayland

```bash
sudo apt install wl-clipboard ydotool
sudo usermod -a -G input $USER
# 重新登录使 input 组生效
```

> 服务会自动通过 `WAYLAND_DISPLAY` / `XDG_SESSION_TYPE` 检测环境，无需手动配置。

### Python 依赖

```bash
conda create -n kaylor_input python=3.10 -y
conda activate kaylor_input
pip install flask
```

## 工作原理

| | X11 | Wayland |
|---|---|---|
| 设置文本 | `xclip -selection primary` | `wl-copy` + `wl-copy --primary` |
| 粘贴 | `xdotool click 2`（中键粘贴） | `ydotool click 3` |
| 选区恢复 | 保存并恢复原有 PRIMARY | — |

两种方案都不依赖键盘快捷键，通过鼠标点击触发粘贴，全应用通用。

## 使用

1. 电脑启动服务 `python app.py`
2. 手机连接同一 WiFi
3. 手机浏览器打开 `http://<电脑IP>:5000`
4. 电脑光标放在需要输入的位置
5. 手机输入文本，点 Send（或 Enter）
6. 文本自动粘贴到电脑光标处
