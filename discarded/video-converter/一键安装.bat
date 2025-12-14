@echo off
chcp 65001 >nul
title 神奇妙妙小工具 - 一键安装程序
color 0A

echo ============================================
echo        神奇妙妙小工具 - 一键安装程序
echo ============================================
echo.
echo 本程序将自动安装以下组件：
echo 1. 🟢 Node.js（JavaScript运行环境）
echo 2. 🎥 FFmpeg（视频处理工具）
echo 3. 📦 项目依赖包
echo 4. 🚀 启动视频转换器
echo.
echo 注意：部分安装需要管理员权限
echo ============================================
echo.

REM 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ 管理员权限已确认
) else (
    echo ⚠️  需要管理员权限来安装FFmpeg
    echo 请右键点击此脚本，选择"以管理员身份运行"
    pause
    exit /b
)

echo.
echo 🔍 检查当前系统环境...
echo.

REM 检查是否已安装Node.js
where node >nul 2>nul
if %errorlevel% equ 0 (
    node --version
    echo ✅ Node.js 已安装
) else (
    echo 📥 正在安装 Node.js...
    echo.
    
    REM 下载并安装Node.js（使用官方安装包）
    echo 正在下载 Node.js 安装包...
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://nodejs.org/dist/v18.18.0/node-v18.18.0-x64.msi', 'nodejs-installer.msi')"
    
    if exist "nodejs-installer.msi" (
        echo 正在安装 Node.js...
        msiexec /i "nodejs-installer.msi" /quiet /qn /norestart ADDLOCAL=ALL
        timeout /t 10 /nobreak >nul
        
        echo 清理安装文件...
        del "nodejs-installer.msi"
        
        echo 更新环境变量...
        setx PATH "%PATH%;C:\Program Files\nodejs\" /M
        
        echo ✅ Node.js 安装完成！
    ) else (
        echo ❌ Node.js 下载失败，请手动安装：
        echo 请访问 https://nodejs.org 下载安装
        pause
        exit /b
    )
)

echo.
REM 检查是否已安装FFmpeg
where ffmpeg >nul 2>nul
if %errorlevel% equ 0 (
    ffmpeg -version | findstr "version"
    echo ✅ FFmpeg 已安装
) else (
    echo 📥 正在安装 FFmpeg...
    echo.
    
    REM 创建FFmpeg安装目录
    if not exist "C:\ffmpeg" mkdir "C:\ffmpeg"
    
    echo 正在下载 FFmpeg...
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip', 'ffmpeg.zip')"
    
    if exist "ffmpeg.zip" (
        echo 正在解压 FFmpeg...
        powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath 'C:\ffmpeg-temp' -Force"
        
        echo 复制文件到安装目录...
        xcopy "C:\ffmpeg-temp\ffmpeg-master-latest-win64-gpl\bin\*" "C:\ffmpeg\" /E /Y /Q
        
        echo 清理临时文件...
        rd /s /q "C:\ffmpeg-temp" 2>nul
        del "ffmpeg.zip"
        
        REM 添加FFmpeg到系统PATH
        echo 添加FFmpeg到系统环境变量...
        setx PATH "%PATH%;C:\ffmpeg" /M
        
        echo ✅ FFmpeg 安装完成！
    ) else (
        echo ❌ FFmpeg 下载失败，使用备用方案...
        
        REM 尝试使用chocolatey安装（如果已安装）
        where choco >nul 2>nul
        if %errorlevel% equ 0 (
            echo 使用Chocolatey安装FFmpeg...
            choco install ffmpeg -y
        ) else (
            echo ⚠️  请手动安装FFmpeg：
            echo 1. 访问 https://ffmpeg.org/download.html
            echo 2. 下载Windows版本
            echo 3. 解压到 C:\ffmpeg
            echo 4. 将 C:\ffmpeg\bin 添加到系统PATH
            pause
        )
    )
)

echo.
echo 🔧 安装项目依赖...
echo.

REM 检查package.json是否存在
if not exist "package.json" (
    echo 初始化项目...
    npm init -y
)

echo 安装Express...
npm install express --save --loglevel=error
echo 安装Multer...
npm install multer --save --loglevel=error
echo 安装其他依赖...
npm install child_process os fs path --save --loglevel=error

echo.
echo 🎉 所有组件安装完成！
echo.

REM 验证安装
echo 🔍 验证安装结果：
echo.
where node && node --version
echo.
where ffmpeg && ffmpeg -version | findstr "version"
echo.
echo 📁 项目文件：
dir /b *.js *.html 2>nul | findstr "." || echo "⚠️  未找到项目文件"

echo.
echo ============================================
echo          安装完成！下一步操作：
echo ============================================
echo.
echo 1. 请确保有以下文件在当前目录：
echo    - backend.js  (后端代码)
echo    - index.html  (前端界面)
echo.
echo 2. 手动启动：
echo    node backend.js
echo.
echo 3. 然后访问：http://localhost:3001
echo.
echo 4. 您也可以运行 "start_app.bat" 启动
echo.

REM 创建启动脚本
echo 创建启动脚本...
echo @echo off > start_app.bat
echo chcp 65001 ^>nul >> start_app.bat
echo echo 正在启动视频转换器... >> start_app.bat
echo node backend.js >> start_app.bat

echo 🚀 创建了启动脚本：start_app.bat
echo.
echo 按任意键启动视频转换器...
pause >nul

REM 启动应用
echo 正在启动视频转换器...
node backend.js