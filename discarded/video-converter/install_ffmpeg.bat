@echo off
echo 正在安装FFmpeg...
echo.

REM 下载FFmpeg（备用链接）
echo 请手动下载FFmpeg：
echo.
echo 方法1：访问 https://ffmpeg.org/download.html
echo 方法2：运行 winget install ffmpeg (Windows 10/11)
echo.
echo 下载后：
echo 1. 解压到 C:\ffmpeg
echo 2. 添加到系统PATH
echo.

echo 请按任意键打开下载页面...
pause
start https://github.com/BtbN/FFmpeg-Builds/releases
