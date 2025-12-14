@echo off
chcp 65001 >nul
title 视频转换器最终版
color 0A
mode con: cols=80 lines=30

echo.
echo ╔══════════════════════════════════════════════╗
echo ║          视频转换器 - 最终版                 ║
echo ╚══════════════════════════════════════════════╝
echo.

echo 正在检查环境...
echo.

REM 检查Node.js
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ✗ 错误: 未安装Node.js
    echo 请从 https://nodejs.org 下载安装
    echo 安装后请重新运行此程序
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do echo ✓ Node.js 版本: %%i
echo.

REM 检查FFmpeg
where ffmpeg >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ! 警告: 未安装FFmpeg
    echo   转换功能将受限，请安装FFmpeg
    echo   推荐运行: install_ffmpeg.bat
    echo.
) else (
    echo ✓ FFmpeg 已安装
    echo.
)

REM 检查依赖
echo 检查项目依赖...
if not exist "node_modules" (
    echo 正在安装依赖包，请稍候...
    call npm install --no-optional > nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo ✗ 依赖安装失败
        echo 请检查网络连接后重试
        pause
        exit /b 1
    )
    echo ✓ 依赖安装完成
) else (
    echo ✓ 依赖包已存在
)
echo.

REM 清理旧的输出文件
echo 清理旧文件...
if exist "output_*" (
    del output_* 2>nul
    echo ✓ 清理输出文件
)
if exist "*.gif" (
    del *.gif 2>nul
)
if exist "*.webp" (
    del *.webp 2>nul
)
echo.

echo 启动服务器...
echo ==========================================
echo.

node app.js

echo.
echo ==========================================
echo 服务器已停止
echo ==========================================
echo.
pause