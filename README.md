# kaylor_input

局域网文本输入中继工具。手机打开网页，输入文本，点击 Send，文本被粘贴到电脑光标位置。自动适配 X11 和 Wayland。

## 构建

```bash
sudo apt install dpkg-dev debhelper
dpkg-buildpackage -us -uc -b
# 生成 ../kaylor-input_1.0.0_all.deb
```

## 安装

```bash
sudo dpkg -i kaylor-input_1.0.0_all.deb
sudo apt install -f   # 补全依赖
```

## 启用

```bash
systemctl --user enable --now kaylor-input
```

开机自启：

```bash
sudo loginctl enable-linger $USER
```

- 本机访问：`http://localhost:5000`
- 手机/其他设备访问：`http://<IP>:5000`（`hostname -I` 查看 IP）

## 依赖

| 包名 | 必须 | 用途 |
|---|---|---|
| `python3-flask` | 是 | Flask Web 服务 |
| `xdotool` | 否 | X11 鼠标/键盘模拟 |
| `xclip` | 否 | X11 剪贴板读写 |
| `wl-clipboard` | 否 | Wayland 剪贴板读写 |
| `ydotool` | 否 | Wayland 输入模拟 |

### X11

```bash
sudo apt install xdotool xclip
```

### Wayland

```bash
sudo apt install wl-clipboard ydotool
sudo usermod -a -G input $USER
# 重新登录使 input 组生效
```

> ydotool 需用户加入 `input` 组才能访问 `/dev/uinput`。

## 工作原理

| | X11 | Wayland |
|---|---|---|
| 设置文本 | `xclip clipboard + primary` | `wl-copy` + `wl-copy --primary` |
| 粘贴 | `xdotool key ctrl+v` | `ydotool key ctrl+v` |

粘贴在键盘焦点（文本光标）位置，而非鼠标指针位置。
