#!/bin/bash
# 织觉引擎 WeaveMind — 一键启动
cd "$(dirname "$0")"

echo "╔══════════════════════════════════════╗"
echo "║     织觉引擎 WeaveMind 启动中...     ║"
echo "╚══════════════════════════════════════╝"

# 杀掉已有进程
lsof -ti:5000 | xargs kill -9 2>/dev/null
lsof -ti:5001 | xargs kill -9 2>/dev/null
lsof -ti:5002 | xargs kill -9 2>/dev/null
lsof -ti:5003 | xargs kill -9 2>/dev/null
lsof -ti:5004 | xargs kill -9 2>/dev/null
sleep 1

# 启动各模块
python3 server.py &
python3 aesthetic-translator/backend/app.py &
python3 spatial-engine/backend/app.py &
python3 trend-prophet/backend/app.py &
python3 textile-gene-editor/backend/app.py &

sleep 2

echo ""
echo "✅ 织觉引擎已启动："
echo "   🏠 入口首页:     http://localhost:5000"
echo "   🎨 审美翻译器:   http://localhost:5004"
echo "   🧬 基因编辑器:   http://localhost:5003"
echo "   🏠 空间感知:     http://localhost:5001"
echo "   📊 趋势先知:     http://localhost:5002"
echo ""
echo "按 Ctrl+C 停止所有服务"
wait