# 技能图标生成工具
***by [ZhuLuOT](https://github.com/ZhuLuOT)***

## 声明
此处仅有脚本文件，不含其它资产。

## 功能简介
这是一个自动化工具，用于将技能图片合成到底图模板上。

## 目录结构

```
├── base/          # 底图模板文件夹
├── skill/         # 技能图片文件夹
├── txt/           # 角色描述文件文件夹
├── output/        # 输出文件夹
├── skill_composer.py  # 主程序文件
└── README.md      # 说明文档
```

## 使用方法

### 基本用法

```bash
python skill_composer.py
```

默认情况下，工具会：
- 从 `base/` 文件夹加载底图模板
- 从 `skill/` 文件夹加载技能图片
- 从 `txt/` 文件夹读取角色描述文件
- 将合成结果输出到 `output/` 文件夹
- 使用自动匹配模式

### 命令行参数

```
-h, --help          显示帮助信息
--base, -b          底图文件夹路径 (默认: base)
--skill, -s         技能图片文件夹路径 (默认: skill)
--output, -o        输出文件夹路径 (默认: output)
--scale, -sc        技能图片缩放比例 (默认: 1.0)
--config, -c        配置文件路径 (JSON格式)
--mapping, -m       底图属性映射配置文件路径 (JSON格式)
--test, -t          创建测试数据并运行测试
```

## 配置文件格式

### 精确组合配置文件 (--config)

```json
{
  "combinations": [
    {
      "base": "寒冷模板.png",
      "skill": "XX-战.png",
      "scale": 0.9
    },
    {
      "base": "灼热模板.png",
      "skill": "XX-普.png"
    }
  ]
}
```

### 自定义映射配置文件 (--mapping)

```json
{
  "mapping": {
    "寒冷伤害": "自定义寒冷模板.png",
    "灼热伤害": "自定义灼热模板.png",
    "新伤害类型": "新模板.png"
  }
}
```

## 工作原理

### 自动匹配模式

1. 从技能图片文件名中提取角色名（格式：角色名-招式名.png）
2. 读取对应的角色描述文件（txt文件夹中）
3. 从角色描述文件中提取战斗技能部分的普通攻击伤害类型
4. 根据伤害类型匹配相应的底图模板
5. 将技能图片合成到底图模板上
6. 保存合成结果

### 支持的伤害类型

- 寒冷伤害
- 灼热伤害
- 物理伤害
- 电磁伤害
- 自然伤害

## 示例

### 使用自动匹配模式

```bash
python skill_composer.py --base base --skill skill --output output --scale 0.9
```

### 使用精确组合模式

```bash
python skill_composer.py --config config.json
```

### 使用自定义映射

```bash
python skill_composer.py --mapping custom_mapping.json
```

## 依赖

- Python 3.x
- Pillow (PIL) 库

## 安装依赖

```bash
pip install pillow
```

## 注意事项

1. 技能图片文件名格式应为：`角色名-招式名.png`
2. 角色描述文件应放在txt文件夹中，文件名应为：`角色名.txt`
3. 角色描述文件中应包含战斗技能部分和普通攻击描述
4. 底图模板文件名应与伤害类型对应（如：寒冷模板.png）

