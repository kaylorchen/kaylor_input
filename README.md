# kaylor_input

局域网文本输入中继工具。手机打开网页，输入文本，点击 Send，文本被粘贴到电脑光标位置。自动适配 X11 和 Wayland。

## 构建 Deb 包

```bash
sudo apt install dpkg-dev debhelper   # 构建工具
dpkg-buildpackage -us -uc -b          # 构建
```

生成的 `kaylor-input_*.deb` 在上级目录。

## 安装

```bash
sudo dpkg -i kaylor-input_1.0.0_all.deb
sudo apt install -f               # 自动安装依赖（python3-flask 等）
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

## 工作原理

| | X11 | Wayland |
|---|---|---|
| 设置文本 | `xclip -selection primary` | `wl-copy` + `wl-copy --primary` |
| 粘贴 | `xdotool click 2`（中键粘贴） | `ydotool click 3` |
| 选区恢复 | 保存并恢复原有 PRIMARY | — |

## 依赖

**Python：** `python3-flask`（必须）

**X11：** `xdotool xclip`

**Wayland：** `wl-clipboard ydotool` + 用户加入 `input` 组并重新登录
