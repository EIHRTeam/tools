from PIL import Image
import os
import glob


current_dir = os.getcwd()

base_dir = os.path.join(current_dir, 'base')
icon_dir = os.path.join(current_dir, 'icon')
output_dir = os.path.join(current_dir, 'output')
os.makedirs(output_dir, exist_ok=True)

base_files = glob.glob(os.path.join(base_dir, '*.png'))
icon_files = glob.glob(os.path.join(icon_dir, '*.png'))
for base_file in base_files:
    base_image = Image.open(base_file)
    base_image = base_image.convert('RGBA')
    base_width, base_height = base_image.size
    base_filename = os.path.basename(base_file)
    base_name = os.path.splitext(base_filename)[0]
    for icon_file in icon_files:
        icon_image = Image.open(icon_file)
        icon_image = icon_image.convert('RGBA')
        icon_width, icon_height = icon_image.size
        icon_filename = os.path.basename(icon_file)
        icon_name = os.path.splitext(icon_filename)[0]
        default_x = (base_width - icon_width) // 2
        default_y = (base_height - icon_height) // 2

        if base_filename in ['四级基质.png', '五级基质.png']:
            position = (default_x + 5, default_y - 4)
        else:
            position = (default_x, default_y)

        result_image = Image.new('RGBA', (base_width, base_height), (0, 0, 0, 0))
        result_image.paste(base_image, (0, 0))
        result_image.paste(icon_image, position, icon_image)

        output_filename = f'{base_name}_{icon_name}.png'
        output_path = os.path.join(output_dir, output_filename)
        result_image.save(output_path)
        
        print(f'已生成: {output_filename}')

print('叠加完成！')
