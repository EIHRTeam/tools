### 📷 批量图片尺寸转换工具
一个简单易用的批量图片尺寸转换工具，支持自定义输入输出尺寸，专为普通用户设计。

***by [oculto](https://github.com/oculto-link)***

## 声明
此处仅有脚本文件，不含其它资产。

## ✨ 功能特点
批量处理：一次性处理多个图片文件

尺寸自定义：自由设置原始尺寸和目标尺寸

智能检测：自动识别图片尺寸并提示

桌面友好：自动在桌面创建专用文件夹

格式支持：JPG, JPEG, PNG, BMP, GIF, TIFF, WebP

简单操作：全中文界面，按提示操作即可

## 📦 安装步骤
1、安装Python
   
需要 Python 3.6 或更高版本

下载地址：https://www.python.org/downloads/

Windows用户安装时务必勾选 "Add Python to PATH"

2、安装依赖库

打开命令提示符（Windows）或终端（Mac/Linux），运行：
```bash
pip install Pillow
```

如遇下载困难请使用以下镜像站进行下载：
```bash
# 使用清华镜像
pip install Pillow -i https://pypi.tuna.tsinghua.edu.cn/simple
```

3、 获取程序

从 Release 下载最新版的 [Image-resizer-tool.zip](https://github.com/EIHRTeam/tools/releases/latest/download/Image-resizer-tool.zip)

## 🚀 使用方法
第一次运行：

双击运行 image_resizer.py

程序会在桌面自动创建文件夹结构：

```
桌面/
└── 图片批量处理/
    ├── 原始图片/       # 放入需要处理的图片
    └── 处理后的图片/   # 输出结果位置
```

处理流程：

1、将需要处理的图片放入 "原始图片" 文件夹

2、重新运行程序

3、程序会自动检测图片尺寸

4、确认或输入原始尺寸

5、输入目标尺寸

6、等待处理完成

## ⚠️ 注意事项
1、图片格式：支持常见图片格式，不支持RAW格式

2、尺寸建议：避免小图片放大超过3倍，可能影响质量

3、内存占用：处理大尺寸图片（超过5000×5000）需要较多内存

4、备份建议：处理前建议备份原始图片

## 🤔 常见问题
Q: 程序打不开怎么办？

A: 请确认：
Python已正确安装并添加到PATH

Pillow库已安装：pip install Pillow

双击运行或使用命令行：python image_resizer.py


Q: 文件夹没有自动创建？

A: 程序会在第一次运行时创建文件夹，如果未创建请手动创建：

在桌面创建"图片批量处理"文件夹

在其中创建"原始图片"和"处理后的图片"文件夹


Q: 图片尺寸检测不准？

A: 如果图片尺寸不一致，程序会列出各种尺寸及数量，请手动输入最常见的尺寸


Q: 处理后的图片质量不好？

A:程序使用高质量缩放算法

小尺寸放大过多会导致质量下降

建议原始图片分辨率不低于目标尺寸的1/3

## 🔧 高级选项
对于需要批量处理不同尺寸图片的用户：

将相同尺寸的图片放在一起处理

分批处理大量图片（建议每次100-200张）

处理前先测试几张确认效果

## 📞 获取帮助
如果遇到问题：

检查Python和Pillow是否正确安装

确认图片格式是否支持

查看程序提示信息

如仍有问题，可在GitHub提交Issue ***(https://github.com/EIHRTeam/tools/issues/new)***
