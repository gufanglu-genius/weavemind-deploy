@echo off
chcp 65001 >nul 2>&1
title 织觉引擎 WeaveMind

echo ========================================
echo     织觉引擎 WeaveMind 启动中...
echo ========================================
echo.

cd /d "%~dp0"

:: 杀掉已有进程
for %%p in (5000 5001 5002 5003 5004) do (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%%p ^| findstr LISTENING') do (
        taskkill /F /PID %%a >nul 2>&1
    )
)
timeout /t 1 /nobreak >nul

:: 启动各模块
echo 启动主站入口 (端口5000)...
start /b python server.py

echo 启动空间感知引擎 (端口5001)...
start /b python spatial-engine\backend\app.py

echo 启动趋势先知引擎 (端口5002)...
start /b python trend-prophet\backend\app.py

echo 启动基因编辑器 (端口5003)...
start /b python textile-gene-editor\backend\app.py

echo 启动审美翻译器 (端口5004)...
start /b python aesthetic-translator\backend\app.py

timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   织觉引擎已启动：
echo   入口首页:     http://localhost:5000
echo   审美翻译器:   http://localhost:5004
echo   基因编辑器:   http://localhost:5003
echo   空间感知:     http://localhost:5001
echo   趋势先知:     http://localhost:5002
echo ========================================
echo.
echo 按任意键停止所有服务...
pause >nul

:: 停止所有进程
for %%p in (5000 5001 5002 5003 5004) do (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%%p ^| findstr LISTENING') do (
        taskkill /F /PID %%a >nul 2>&1
    )
)
echo 已停止所有服务。