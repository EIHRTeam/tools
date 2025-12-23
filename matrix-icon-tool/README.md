# 基质叠加工具

这是一个Python脚本，用于将base文件夹中的图片作为底图，将icon文件夹中的图片叠加在底图上生成新的图片。

## 功能说明

- 将base文件夹中的每张底图与icon文件夹中的每张图标图片进行叠加组合
- 生成的图片保存在output文件夹中
- 特殊处理：对于命名为"四级基质.png"和"五级基质.png"的图片，图标会在居中位置基础上进行微调

## 目录结构

```
photo2/
├── base/           # 底图文件夹
├── icon/           # 图标文件夹
├── output/         # 输出文件夹（自动创建）
├── merge_images.py # 主脚本文件
└── README.md       # 说明文档
```

## 安装依赖

脚本需要使用Pillow库进行图像处理：

```bash
pip install pillow
```

## 使用方法

1. 将底图图片放入`base`文件夹
2. 将图标图片放入`icon`文件夹
3. 运行脚本：

```bash
python merge_images.py
```

4. 生成的图片将保存在`output`文件夹中，文件名格式为：`底图名称_图标名称.png`

## 特殊处理逻辑

对于底图为"四级基质.png"和"五级基质.png"的情况，图标位置会在默认居中位置基础上进行调整：
- X轴：增加5px
- Y轴：减少4px

这种调整是为了确保在这些特定底图上图标位置更加合适。

## 注意事项

1. 确保底图和图标图片都是PNG格式
2. 脚本会自动处理图片的透明度
3. 如果output文件夹不存在，脚本会自动创建
4. 生成的图片数量 = 底图数量 × 图标数量

## 示例

假设有以下文件结构：

```
base/
├── background1.png
├── 四级基质.png
icon/
├── logo1.png
├── logo2.png
```

运行脚本后，output文件夹将包含：
```
output/
├── background1_logo1.png
├── background1_logo2.png
├── 四级基质_logo1.png
├── 四级基质_logo2.png
```

其中，"四级基质_logo1.png"和"四级基质_logo2.png"中的图标位置会进行特殊调整。

