#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量图片尺寸转换工具
功能：批量修改图片尺寸，支持自定义原始尺寸和目标尺寸
使用方法：只需运行脚本，按提示操作即可
"""

import os
import sys
from PIL import Image
from pathlib import Path

def get_desktop_path():
    # 获取用户主目录
    home = Path.home()
    
    # 不同操作系统的桌面路径
    if sys.platform == "win32":
        # Windows
        desktop = home / "Desktop"
    elif sys.platform == "darwin":
        # macOS
        desktop = home / "Desktop"
    else:
        # Linux
        desktop = home / "Desktop"
        # 如果Linux没有Desktop文件夹，尝试其他可能的位置
        if not desktop.exists():
            desktop = home / "桌面"  # 中文桌面
            if not desktop.exists():
                # 如果还是没有，就使用用户主目录
                desktop = home
    
    # 如果桌面文件夹不存在，创建它
    if not desktop.exists():
        desktop.mkdir(parents=True, exist_ok=True)
    
    return desktop

def detect_image_sizes(folder_path):
    """
    检测文件夹中所有图片的尺寸
    返回：尺寸列表，每个元素为(宽度, 高度)
    """
    supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']
    sizes = []
    
    for image_file in folder_path.iterdir():
        if not image_file.is_file():
            continue
        
        # 检查文件格式是否支持
        if image_file.suffix.lower() not in supported_formats:
            continue
        
        try:
            with Image.open(image_file) as img:
                sizes.append(img.size)
        except Exception as e:
            print(f"  警告：无法读取图片 {image_file.name}，错误：{e}")
            continue
    
    return sizes

def get_original_size_from_user(autodetected_size=None):
    """
    让用户输入原始图片尺寸
    如果提供了自动检测的尺寸，会先询问用户是否使用该尺寸
    """
    # 如果有自动检测的尺寸，先询问用户是否使用
    if autodetected_size:
        print(f"\n🔍 自动检测到图片尺寸：{autodetected_size[0]} × {autodetected_size[1]}")
        choice = input("是否使用此尺寸作为原始尺寸？(y=使用, n=手动输入): ").strip().lower()
        if choice == 'y':
            print(f"✅ 已使用自动检测尺寸：{autodetected_size[0]} × {autodetected_size[1]}")
            return autodetected_size
    
    # 手动输入尺寸
    while True:
        try:
            print("\n📐 请输入原始图片尺寸")
            print("-" * 30)
            original_width = input("原始图片宽度(像素): ").strip()
            original_height = input("原始图片高度(像素): ").strip()
            
            # 转换为整数
            original_width = int(original_width)
            original_height = int(original_height)
            
            # 验证尺寸是否合理
            if original_width <= 0 or original_height <= 0:
                print("❌ 错误：尺寸必须是正数，请重新输入")
                continue
            elif original_width > 10000 or original_height > 10000:
                print("❌ 错误：尺寸过大，请确认输入正确")
                continue
                
            print(f"✅ 设置成功：原始尺寸为 {original_width} × {original_height} 像素")
            return (original_width, original_height)
            
        except ValueError:
            print("❌ 错误：请输入有效的数字")
        except KeyboardInterrupt:
            print("\n👋 用户取消操作")
            sys.exit(0)

def get_target_size_from_user():
    """
    让用户输入目标图片尺寸
    """
    while True:
        try:
            print("\n🎯 请输入目标图片尺寸")
            print("-" * 30)
            target_width = input("目标图片宽度(像素): ").strip()
            target_height = input("目标图片高度(像素): ").strip()
            
            # 转换为整数
            target_width = int(target_width)
            target_height = int(target_height)
            
            # 验证尺寸是否合理
            if target_width <= 0 or target_height <= 0:
                print("❌ 错误：尺寸必须是正数，请重新输入")
                continue
            elif target_width > 20000 or target_height > 20000:
                print("⚠️  警告：目标尺寸非常大，这可能会消耗大量内存")
                confirm = input("是否继续？(y/n): ").strip().lower()
                if confirm != 'y':
                    continue
            
            print(f"✅ 设置成功：目标尺寸为 {target_width} × {target_height} 像素")
            return (target_width, target_height)
            
        except ValueError:
            print("❌ 错误：请输入有效的数字")
        except KeyboardInterrupt:
            print("\n👋 用户取消操作")
            sys.exit(0)

def resize_single_image(input_path, output_path, original_size, target_size):
    """
    处理单张图片：调整尺寸
    
    参数说明:
        input_path: 需要处理的图片文件路径
        output_path: 处理完成后保存的路径
        original_size: 用户指定的原始图片尺寸（宽度, 高度）
        target_size: 用户想要调整到的目标尺寸（宽度, 高度）
    """
    try:
        # 1. 打开图片文件
        with Image.open(input_path) as img:
            # 2. 获取图片实际尺寸
            actual_size = img.size
            print(f"📄 正在处理: {input_path.name}")
            print(f"   📏 图片实际尺寸: {actual_size[0]} × {actual_size[1]}")
            
            # 3. 检查图片实际尺寸是否与用户指定的原始尺寸一致
            if actual_size != original_size:
                print(f"   ⚠️  注意：图片实际尺寸与指定的原始尺寸不一致")
                print(f"   指定的原始尺寸: {original_size[0]} × {original_size[1]}")
                
                # 询问用户是否继续
                choice = input("   是否继续处理？(y=继续, n=跳过): ").strip().lower()
                if choice != 'y':
                    print("   ⏭️  已跳过此图片")
                    return False
            
            # 4. 调整图片尺寸（使用高质量算法）
            #    LANCZOS 算法能保持图片清晰度，减少锯齿
            try:
                resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
            except AttributeError:
                # 兼容旧版本Pillow
                resized_img = img.resize(target_size, Image.ANTIALIAS)
            
            # 5. 保存处理后的图片
            #    保持图片原来的格式和质量
            file_extension = output_path.suffix.lower()
            
            # 如果是透明图片（如PNG），保留透明度
            if resized_img.mode in ('RGBA', 'LA', 'P'):
                resized_img.save(output_path)
            # 如果是JPEG图片，设置高质量保存
            elif file_extension in ['.jpg', '.jpeg']:
                resized_img.save(output_path, quality=95, optimize=True)
            # 其他格式图片
            else:
                resized_img.save(output_path)
            
            # 6. 显示处理结果
            print(f"   ✅ 处理完成：{actual_size} → {target_size}")
            print(f"   💾 已保存到: {output_path}")
            return True
            
    # 错误处理：如果图片打不开或处理出错
    except Exception as e:
        print(f"   ❌ 处理失败：{str(e)}")
        return False

def wait_for_images(input_folder):
    """
    等待用户在文件夹中放入图片
    """
    print(f"\n📁 检测到 '{input_folder.name}' 文件夹中没有图片")
    print("   请将需要处理的图片放入此文件夹")
    print("\n   支持的图片格式:")
    print("   JPG, JPEG, PNG, BMP, GIF, TIFF, WebP")
    
    while True:
        print(f"\n   当前文件夹位置: {input_folder}")
        choice = input("\n   放入图片后，请选择：\n   1 = 我已放入图片，重新扫描\n   2 = 退出程序\n   请选择 (1/2): ").strip()
        
        if choice == '1':
            # 重新扫描文件夹
            if any(input_folder.iterdir()):
                return True
            else:
                print("\n   ❌ 文件夹仍然是空的，请确认已放入图片")
                print("   注意：请直接将图片文件放入文件夹，不要新建子文件夹")
        elif choice == '2':
            print("\n👋 程序退出")
            return False
        else:
            print("   ❌ 请输入 1 或 2")

def batch_resize_images():
    """
    批量处理图片的主函数
    """
    print("=" * 50)
    print("📷 批量图片尺寸转换工具")
    print("=" * 50)
    
    # 1. 获取桌面路径
    desktop = get_desktop_path()
    
    # 2. 设置固定的文件夹结构
    #    所有图片都放在桌面的 "图片批量处理" 文件夹中
    base_folder = desktop / "图片批量处理"
    input_folder = base_folder / "原始图片"
    output_folder = base_folder / "处理后的图片"
    
    # 3. 确保必要的文件夹存在
    input_folder.mkdir(parents=True, exist_ok=True)
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # 4. 显示文件夹信息给用户
    print(f"\n📁 文件夹设置：")
    print(f"   原始图片位置：{input_folder}")
    print(f"   处理后图片位置：{output_folder}")
    print(f"\n💡 使用说明：")
    print(f"   1. 将需要处理的图片放入 '{input_folder.name}' 文件夹")
    print(f"   2. 按提示输入原始尺寸和目标尺寸")
    print(f"   3. 处理完成后在 '{output_folder.name}' 文件夹查看结果")
    
    # 5. 检查原始图片文件夹是否有图片
    #    如果没有图片，等待用户放入
    if not any(input_folder.iterdir()):
        if not wait_for_images(input_folder):
            return
    
    # 6. 自动检测图片尺寸，看看是否所有图片尺寸一致
    print(f"\n🔍 正在扫描图片尺寸...")
    image_sizes = detect_image_sizes(input_folder)
    
    if not image_sizes:
        print("❌ 文件夹中没有找到支持的图片文件")
        print("   请确认放入的是支持的图片格式")
        input("按回车键退出...")
        return
    
    # 7. 检查所有图片尺寸是否一致
    autodetected_size = None
    if image_sizes:
        # 获取第一个图片的尺寸
        first_size = image_sizes[0]
        all_same = all(size == first_size for size in image_sizes)
        
        if all_same:
            print(f"✅ 检测到所有图片尺寸一致：{first_size[0]} × {first_size[1]}")
            autodetected_size = first_size
        else:
            print("⚠️  检测到图片尺寸不一致：")
            unique_sizes = {}
            for size in image_sizes:
                key = f"{size[0]}×{size[1]}"
                unique_sizes[key] = unique_sizes.get(key, 0) + 1
            
            for size_str, count in unique_sizes.items():
                print(f"   {size_str} 像素: {count} 张")
            print("\n   ⚠️  注意：图片尺寸不一致可能会导致处理错误")
    
    # 8. 让用户输入原始图片尺寸
    original_size = get_original_size_from_user(autodetected_size)
    
    # 9. 让用户输入目标图片尺寸
    target_size = get_target_size_from_user()
    
    # 10. 统计信息
    processed_count = 0
    skipped_count = 0
    failed_count = 0
    
    print(f"\n🚀 开始处理图片...")
    print("-" * 50)
    
    # 11. 支持的图片格式
    supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']
    
    # 12. 遍历文件夹中的所有图片文件
    for image_file in input_folder.iterdir():
        # 只处理文件，不处理文件夹
        if not image_file.is_file():
            continue
        
        # 检查文件格式是否支持
        if image_file.suffix.lower() not in supported_formats:
            print(f"⏭️  跳过 {image_file.name}：不支持此格式")
            skipped_count += 1
            continue
        
        # 构建输出文件路径（保持原文件名）
        output_file = output_folder / image_file.name
        
        # 处理图片
        success = resize_single_image(image_file, output_file, original_size, target_size)
        
        # 更新统计
        if success:
            processed_count += 1
        else:
            failed_count += 1
    
    # 13. 显示处理结果
    print("-" * 50)
    print("🎉 批量处理完成！")
    print(f"   成功处理：{processed_count} 张")
    print(f"   处理失败：{failed_count} 张")
    print(f"   跳过文件：{skipped_count} 张")
    print(f"\n📁 处理后的图片保存在：{output_folder}")
    print("\n提示：")
    print("   1. 如果需要处理更多图片，只需将新图片放入原始文件夹重新运行程序")
    print("   2. 如果要处理不同尺寸的图片，需要重新运行程序并输入新的尺寸")
    
    # 14. 等待用户确认
    input("\n按回车键退出程序...")

def main():
    """
    程序主入口
    """
    try:
        # 检查是否安装了必要的库
        try:
            from PIL import Image
        except ImportError:
            print("❌ 缺少必要的库：Pillow")
            print("请先安装：pip install Pillow")
            input("按回车键退出...")
            sys.exit(1)
        
        # 运行批量处理
        batch_resize_images()
        
    except KeyboardInterrupt:
        print("\n\n👋 用户中断操作，程序退出")
    except Exception as e:
        print(f"\n❌ 程序运行出错：{str(e)}")
        print("请检查：")
        print("   1. 图片文件是否损坏")
        print("   2. 是否有足够的磁盘空间")
        print("   3. 图片尺寸是否过大")
        input("按回车键退出...")

# 程序从这里开始运行
if __name__ == "__main__":
    main()