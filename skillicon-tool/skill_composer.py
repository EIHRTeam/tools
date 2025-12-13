#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能图片与底图合成工具

功能：
- 自动将skill文件夹中的技能图片合成到base文件夹中的底图上
- 支持批量处理
- 可自定义合成位置和大小
- 支持多种图片格式
- 支持配置文件指定技能与底图的对应关系
"""

import os
import json
import argparse
from PIL import Image


def load_images(folder_path, extensions=['.png', '.jpg', '.jpeg', '.bmp']):
    """加载指定文件夹中的所有图片"""
    images = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            _, ext = os.path.splitext(file_name.lower())
            if ext in extensions:
                try:
                    img = Image.open(file_path)
                    images.append((file_name, img))
                    print(f"✓ 加载图片: {file_name}")
                except Exception as e:
                    print(f"✗ 加载失败: {file_name} - {e}")
    return images


def composite_images(base_img, skill_img, position='center', scale=1.0):
    """将技能图片合成到底图上"""
    # 确保技能图片有透明度通道
    if skill_img.mode != 'RGBA':
        skill_img = skill_img.convert('RGBA')
    
    # 调整技能图片大小
    if scale != 1.0:
        new_size = (int(skill_img.width * scale), int(skill_img.height * scale))
        skill_img = skill_img.resize(new_size, Image.Resampling.LANCZOS)
    
    # 计算合成位置
    if position == 'center':
        x = (base_img.width - skill_img.width) // 2
        y = (base_img.height - skill_img.height) // 2
    else:
        # 支持自定义位置 (x, y)
        x, y = position
    
    # 创建合成结果
    result = base_img.copy()
    result.paste(skill_img, (x, y), skill_img)
    
    # 调整最终输出尺寸为204x204像素
    result = result.resize((204, 204), Image.Resampling.LANCZOS)
    
    return result


def load_config(config_path):
    """加载配置文件"""
    if not os.path.exists(config_path):
        print(f"⚠️ 配置文件不存在: {config_path}")
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✓ 加载配置文件: {config_path}")
        return config
    except json.JSONDecodeError as e:
        print(f"✗ 配置文件格式错误: {e}")
        return None
    except Exception as e:
        print(f"✗ 加载配置文件失败: {e}")
        return None


def extract_damage_type(character_name, skill_type=None, txt_folder='txt'):
    """从角色的txt文件中提取指定技能类型的伤害类型"""
    txt_path = os.path.join(txt_folder, f"{character_name}.txt")
    
    if not os.path.exists(txt_path):
        print(f"⚠️ 未找到角色描述文件: {txt_path}")
        return None
    
    # 尝试使用多种编码读取文件
    encodings = ['utf-8', 'gbk', 'gb2312']
    content = None
    
    for enc in encodings:
        try:
            with open(txt_path, 'r', encoding=enc) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"✗ 使用{enc}编码读取{character_name}.txt失败: {e}")
            continue
    
    if content is None:
        print(f"⚠️ 无法读取文件: {txt_path} (尝试了编码: {', '.join(encodings)})")
        return None
    
    def find_skill_damage_type(current_skill_type):
        """根据技能类型查找对应章节并提取伤害类型"""
        # 查找战斗技能部分的起始位置
        combat_skills_start = content.find("【战斗技能 (Combat Skills)】")
        if combat_skills_start == -1:
            # 尝试查找不带英文的版本
            combat_skills_start = content.find("【战斗技能】")
            if combat_skills_start == -1:
                print(f"⚠️ 未在{character_name}.txt中找到战斗技能部分")
                return None
        
        # 根据技能类型定位对应的技能章节
        skill_section_start = None
        
        if current_skill_type == "战" or current_skill_type == "战斗技能":
            # 查找战技章节（第一个非普通攻击的战斗技能）
            # 先找到普通攻击的位置
            normal_attack_start = content.find(">>> 【普通攻击】", combat_skills_start)
            if normal_attack_start == -1:
                print(f"⚠️ 未在{character_name}.txt中找到普通攻击描述")
                return None
            
            # 然后找到下一个技能，即战技
            skill_section_start = content.find(">>> 【", normal_attack_start + 1)
            if skill_section_start == -1:
                print(f"⚠️ 未在{character_name}.txt中找到战斗技能描述")
                return None
                
        elif current_skill_type == "连" or current_skill_type == "连携技":
            # 查找连携技章节
            skill_section_start = content.find("【连携技】")
            if skill_section_start == -1:
                print(f"⚠️ 未在{character_name}.txt中找到连携技描述")
                return None
                
        elif current_skill_type == "终" or current_skill_type == "终结技":
            # 查找终结技章节
            skill_section_start = content.find("【终结技】")
            if skill_section_start == -1:
                print(f"⚠️ 未在{character_name}.txt中找到终结技描述")
                return None
                
        elif current_skill_type == "普" or current_skill_type == "普通攻击":
            # 查找普通攻击章节
            skill_section_start = content.find(">>> 【普通攻击】", combat_skills_start)
            if skill_section_start == -1:
                print(f"⚠️ 未在{character_name}.txt中找到普通攻击描述")
                return None
                
        else:  # 默认提取普通攻击的伤害类型
            skill_section_start = content.find(">>> 【普通攻击】", combat_skills_start)
            if skill_section_start == -1:
                print(f"⚠️ 未在{character_name}.txt中找到普通攻击描述")
                return None
        
        # 查找描述文本
        description_start = content.find("描述:", skill_section_start)
        if description_start == -1:
            print(f"⚠️ 未在{character_name}.txt中找到{current_skill_type}描述")
            return None
        
        # 提取描述文本直到下一个技能或章节
        next_section_start = content.find(">>> 【", description_start)
        if next_section_start == -1:
            # 如果没有下一个技能，查找下一个主要章节
            next_section_start = content.find("【", description_start + 1)
            if next_section_start == -1:
                description = content[description_start:]
            else:
                description = content[description_start:next_section_start]
        else:
            description = content[description_start:next_section_start]
        
        # 提取伤害类型
        damage_types = ["寒冷伤害", "灼热伤害", "物理伤害", "电磁伤害", "自然伤害"]
        for damage_type in damage_types:
            if damage_type in description:
                return damage_type
        
        print(f"⚠️ 未在{character_name}.txt中识别出{current_skill_type}的伤害类型")
        return None
    
    try:
        # 尝试查找指定技能类型的伤害类型
        if skill_type:
            damage_type = find_skill_damage_type(skill_type)
            if damage_type:
                return damage_type
        
        # 回退机制：尝试其他技能类型
        fallback_order = []
        
        if skill_type == "战":
            fallback_order = ["连", "终", "普"]
        elif skill_type == "连":
            fallback_order = ["战", "终", "普"]
        elif skill_type == "终":
            fallback_order = ["战", "连", "普"]
        elif skill_type == "普":
            fallback_order = ["战", "连", "终"]
        else:
            # 默认回退顺序
            fallback_order = ["战", "连", "终", "普"]
        
        print(f"🔄 尝试从其他技能类型获取{character_name}的伤害类型作为回退")
        
        for fallback_skill in fallback_order:
            print(f"   尝试{fallback_skill}技能...")
            damage_type = find_skill_damage_type(fallback_skill)
            if damage_type:
                print(f"✅ 回退成功：使用{fallback_skill}技能的{damage_type}")
                return damage_type
        
        print(f"❌ 所有回退尝试失败，无法获取{character_name}的伤害类型")
        return None
        
    except Exception as e:
        print(f"✗ 提取{character_name}的伤害类型失败: {e}")
        return None


def get_template_mapping(custom_mapping=None):
    """获取伤害类型与底图模板的映射关系"""
    # 默认映射关系
    default_mapping = {
        "寒冷伤害": "寒冷模板.png",
        "灼热伤害": "灼热模板.png",
        "物理伤害": "物理模板.png",
        "电磁伤害": "电磁模板.png",
        "自然伤害": "自然模板.png"
    }
    
    # 如果提供了自定义映射，则合并
    if custom_mapping:
        default_mapping.update(custom_mapping)
    
    return default_mapping


def process_images(base_folder, skill_folder, output_folder, scale=1.0, config=None, custom_mapping=None):
    """批量处理图片合成"""
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    
    # 加载所有底图和技能图片
    base_images = load_images(base_folder)
    skill_images = load_images(skill_folder)
    
    if not base_images:
        print("⚠️ 未找到底图，请确保base文件夹中有图片")
        return
    
    if not skill_images:
        print("⚠️ 未找到技能图片，请确保skill文件夹中有图片")
        return
    
    print(f"\n开始合成图片...")
    print(f"底图数量: {len(base_images)}")
    print(f"技能图片数量: {len(skill_images)}")
    
    # 将图片列表转换为字典，便于查找
    base_dict = {name: img for name, img in base_images}
    skill_dict = {name: img for name, img in skill_images}
    
    # 处理合成任务
    if config and 'combinations' in config:
        # 使用配置文件中的组合
        combinations = config['combinations']
        print(f"\n📋 使用配置文件中的组合（共{len(combinations)}组）")
        
        for i, combo in enumerate(combinations, 1):
            if 'base' not in combo or 'skill' not in combo:
                print(f"✗ 组合 #{i} 缺少必要参数 'base' 或 'skill'")
                continue
            
            base_name = combo['base']
            skill_name = combo['skill']
            combo_scale = combo.get('scale', scale)  # 使用组合特定的缩放比例
            
            # 检查底图和技能图片是否存在
            if base_name not in base_dict:
                print(f"✗ 组合 #{i} 底图不存在: {base_name}")
                continue
            if skill_name not in skill_dict:
                print(f"✗ 组合 #{i} 技能图片不存在: {skill_name}")
                continue
            
            try:
                # 合成图片
                result = composite_images(base_dict[base_name], skill_dict[skill_name], scale=combo_scale)
                
                # 生成输出文件名
                base_name_no_ext, _ = os.path.splitext(base_name)
                skill_name_no_ext, _ = os.path.splitext(skill_name)
                output_name = f"{base_name_no_ext}_{skill_name_no_ext}.png"
                output_path = os.path.join(output_folder, output_name)
                
                # 保存结果
                result.save(output_path, format='PNG')
                print(f"✓ 组合 #{i}: {output_name}")
                
            except Exception as e:
                print(f"✗ 组合 #{i} 合成失败: {base_name} + {skill_name} - {e}")
    else:
        # 自动匹配模式：根据角色技能属性匹配底图
        print(f"\n📋 使用自动匹配模式")
        template_mapping = get_template_mapping(custom_mapping)
        count = 0
        total = len(skill_images)
        
        for skill_name, skill_img in skill_images:
            count += 1
            try:
                # 从技能图片文件名中提取角色名和技能类型（格式：角色名-类型.png）
                if '-' in skill_name:
                    character_name = skill_name.split('-')[0]
                    # 提取技能类型（战、连、普、终等）
                    skill_type = skill_name.split('-')[1].split('.')[0]
                else:
                    print(f"⚠️ 无法从{skill_name}中提取角色名和技能类型")
                    continue
                
                # 提取角色的伤害类型
                damage_type = extract_damage_type(character_name, skill_type)
                if not damage_type:
                    continue
                
                # 匹配底图模板
                if damage_type not in template_mapping:
                    print(f"⚠️ 未知的伤害类型: {damage_type}")
                    continue
                
                # 对于终结技，使用带-终后缀的模板
                base_name = template_mapping[damage_type]
                if skill_type == "终":
                    # 构建终结技模板名称
                    base_name_no_ext, ext = os.path.splitext(base_name)
                    ultimate_base_name = f"{base_name_no_ext}-终{ext}"
                    if ultimate_base_name in base_dict:
                        base_name = ultimate_base_name
                        print(f"🔄 终结技使用专用模板: {base_name}")
                
                if base_name not in base_dict:
                    print(f"⚠️ 未找到对应的底图模板: {base_name}")
                    continue
                
                # 合成图片
                result = composite_images(base_dict[base_name], skill_img, scale=scale)
                
                # 生成输出文件名
                base_name_no_ext, _ = os.path.splitext(base_name)
                skill_name_no_ext, _ = os.path.splitext(skill_name)
                output_name = f"{base_name_no_ext}_{skill_name_no_ext}.png"
                output_path = os.path.join(output_folder, output_name)
                
                # 保存结果
                result.save(output_path, format='PNG')
                print(f"✓ ({count}/{total}) {output_name} (自动匹配: {damage_type} → {base_name})")
                
            except Exception as e:
                print(f"✗ ({count}/{total}) {skill_name} - {e}")
    
    print(f"\n✅ 所有合成任务完成！")
    print(f"输出文件夹: {output_folder}")



def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="技能图片与底图合成工具")
    parser.add_argument('--base', '-b', default='base', help='底图文件夹路径')
    parser.add_argument('--skill', '-s', default='skill', help='技能图片文件夹路径')
    parser.add_argument('--output', '-o', default='output', help='输出文件夹路径')
    parser.add_argument('--scale', '-sc', type=float, default=0.9, help='技能图片缩放比例（最小0.8）')
    parser.add_argument('--config', '-c', default=None, help='配置文件路径（JSON格式）')
    parser.add_argument('--mapping', '-m', default=None, help='底图属性映射配置文件路径（JSON格式）')
    parser.add_argument('--test', '-t', action='store_true', help='创建测试数据并运行测试')
    
    args = parser.parse_args()
    
    # 验证缩放比例
    if args.scale < 0.8:
        print(f"⚠️ 缩放比例不能小于0.8，当前设置为{args.scale}，自动调整为0.8")
        args.scale = 0.8
    
    # 测试模式
    if args.test:
        create_test_data()
    
    print("=" * 50)
    print("技能图片与底图合成工具 v1.0")
    print("=" * 50)
    print(f"底图文件夹: {args.base}")
    print(f"技能图片文件夹: {args.skill}")
    print(f"输出文件夹: {args.output}")
    print(f"技能图片缩放比例: {args.scale}")
    
    # 加载配置文件
    config = None
    if args.config:
        config = load_config(args.config)
        if config:
            print(f"配置文件: {args.config}")
    
    # 加载自定义映射配置
    custom_mapping = None
    if args.mapping:
        mapping_config = load_config(args.mapping)
        if mapping_config and 'mapping' in mapping_config:
            custom_mapping = mapping_config['mapping']
            print(f"底图映射配置: {args.mapping}")
    
    print("=" * 50)
    
    # 执行合成任务
    process_images(args.base, args.skill, args.output, scale=args.scale, config=config, custom_mapping=custom_mapping)


if __name__ == "__main__":
    main()
