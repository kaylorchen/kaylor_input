# kaylor_input

局域网文本输入中继工具。手机打开网页，输入文本，点击 Send，文本会被输入到电脑光标所在位置。

## 启动

```bash
cd /home/kaylor/work/kaylor_input
conda activate kaylor_input
python app.py
```

启动后：
- 本机访问：`http://localhost:5000`
- 手机/其他设备访问：`http://192.168.8.12:5000`（IP 可能变化，用 `hostname -I` 查看当前 IP）

## 依赖

- Python 3.10 + Flask
- xdotool（键盘模拟，已安装）
