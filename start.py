"""
织觉引擎 WeaveMind — 跨平台启动脚本
兼容 Windows / macOS / Linux
"""
import subprocess
import sys
import os
import time
import signal

BASE = os.path.dirname(os.path.abspath(__file__))

PORTS = [5000, 5001, 5002, 5003, 5004]

SERVICES = [
    {"name": "主站入口",       "port": 5000, "script": "server.py"},
    {"name": "空间感知引擎",   "port": 5001, "script": os.path.join("spatial-engine", "backend", "app.py")},
    {"name": "趋势先知引擎",   "port": 5002, "script": os.path.join("trend-prophet", "backend", "app.py")},
    {"name": "基因编辑器",     "port": 5003, "script": os.path.join("textile-gene-editor", "backend", "app.py")},
    {"name": "审美翻译器",     "port": 5004, "script": os.path.join("aesthetic-translator", "backend", "app.py")},
]


def kill_port(port):
    """杀掉占用指定端口的进程"""
    if sys.platform == "win32":
        # Windows
        try:
            result = subprocess.run(
                ["netstat", "-aon"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    pid = parts[-1]
                    subprocess.run(["taskkill", "/F", "/PID", pid],
                                   capture_output=True, timeout=5)
        except Exception:
            pass
    else:
        # macOS / Linux
        try:
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True, text=True, timeout=5
            )
            pids = result.stdout.strip().split()
            for pid in pids:
                if pid.isdigit():
                    os.kill(int(pid), signal.SIGKILL)
        except Exception:
            pass


def cleanup():
    """停止所有服务"""
    print("\n正在停止所有服务...")
    for port in PORTS:
        kill_port(port)
    print("已停止所有服务。")


def main():
    print("=" * 44)
    print("     织觉引擎 WeaveMind 启动中...")
    print("=" * 44)
    print()

    # 杀掉已有进程
    for port in PORTS:
        kill_port(port)
    time.sleep(1)

    processes = []
    for svc in SERVICES:
        script_path = os.path.join(BASE, svc["script"])
        if not os.path.exists(script_path):
            print(f"  [跳过] {svc['name']} — 文件不存在: {svc['script']}")
            continue
        print(f"  启动 {svc['name']} (端口{svc['port']})...")
        p = subprocess.Popen(
            [sys.executable, script_path],
            cwd=BASE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        processes.append(p)

    time.sleep(2)

    print()
    print("=" * 44)
    print("  织觉引擎已启动：")
    print("    入口首页:     http://localhost:5000")
    print("    审美翻译器:   http://localhost:5004")
    print("    基因编辑器:   http://localhost:5003")
    print("    空间感知:     http://localhost:5001")
    print("    趋势先知:     http://localhost:5002")
    print("=" * 44)
    print()
    print("按 Ctrl+C 停止所有服务")

    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()