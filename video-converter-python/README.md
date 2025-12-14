
## 项目简介
这是一个基于 PyQt6 的图形界面应用程序，主要用于处理音视频相关任务。项目中包含 FFmpeg 工具，用于支持音视频处理功能。

***by [oculto](https://github.com/oculto-link)***

## 声明

此处仅有脚本文件，不含其它资产。

## 主要文件说明

video-converter.py：主程序入口文件

ffmpeg.7z：FFmpeg 工具压缩包（解压后用于音视频处理）

requirements.txt：依赖文件（本项目只需安装 PyQt6，此文件仅供参考）

## 运行准备

# 第一步：安装必要的库

请先安装 PyQt6 库，这是本程序运行所必需的：

打开命令提示符（Windows）或终端（Mac/Linux），运行：

```bash
pip install pyqt6
```

如遇下载困难请使用以下镜像站进行下载：
```bash
pip install PyQt6 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

# 第二步：解压并放置 FFmpeg 文件

解压 ffmpeg.7z 文件，你会得到三个文件

将这三个文件与 main.py 放在同一个文件夹中

正确的文件夹目录结构应该如下所示：

```
你的项目文件夹/
├── main.py
├── ffmpeg.exe        (或 ffmpeg 可执行文件)
└── requirements.txt  (无需使用)
```

# 第三步：运行程序

确保所有文件都在同一文件夹后，运行主程序文件：

```bash
python main.py
```

## 使用说明

确保已安装 PyQt6 库

确保 FFmpeg 的三个文件已正确解压并与 main.py 在同一文件夹

运行 main.py 启动图形界面程序

## 注意事项

本程序需要 PyQt6 环境支持

FFmpeg 工具是程序正常运行的必要组件，必须与主程序在同一目录

requirements.txt 文件无需使用但必须要有，本项目只需安装 PyQt6

## 获取帮助

如果遇到问题：

检查自己有无携带脑子

如仍有问题，可在GitHub提交Issue ***(https://github.com/EIHRTeam/tools/issues/new)***
