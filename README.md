# kaylor_input

局域网文本输入中继工具。手机打开网页，输入文本，点击 Send，文本被粘贴到电脑光标位置。自动适配 X11 和 Wayland。

## 安装（Debian 包）

```bash
sudo dpkg -i kaylor-input_1.0.0_all.deb
sudo apt install -f          # 自动安装依赖
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

## 打包

```bash
# 修改版本后重新打包
dpkg-deb --build /tmp/kaylor-deb kaylor-input_1.0.0_all.deb
```

## 工作原理

| | X11 | Wayland |
|---|---|---|
| 设置文本 | `xclip -selection primary` | `wl-copy` + `wl-copy --primary` |
| 粘贴 | `xdotool click 2`（中键粘贴） | `ydotool click 3` |
| 选区恢复 | 保存并恢复原有 PRIMARY | — |

## 依赖

- `python3-flask`（必须）
- `xdotool xclip`（X11）
- `wl-clipboard ydotool`（Wayland）
- Wayland 需将用户加入 `input` 组并重新登录
