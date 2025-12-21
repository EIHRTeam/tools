import cv2
import numpy as np
import os
import glob

def process_dual_outputs(original_path, template_path, output_res_path, output_fixed_path):
    img_orig = cv2.imread(original_path, cv2.IMREAD_UNCHANGED)
    img_temp = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    
    if img_orig is None or img_temp is None:
        return False

    def to_gray(img):
        if len(img.shape) == 3:
            if img.shape[2] == 4:
                return cv2.cvtColor(img[:,:,:3], cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    gray_orig = to_gray(img_orig)
    gray_temp = to_gray(img_temp)

    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(gray_temp, None)
    kp2, des2 = sift.detectAndCompute(gray_orig, None)

    if des1 is None or des2 is None:
        return False

    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    good = [m for m, n in matches if m.distance < 0.7 * n.distance]

    if len(good) < 10:
        return False

    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    M, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    if M is None:
        return False

    h_temp, w_temp = gray_temp.shape[:2]
    pts = np.float32([[0, 0], [0, h_temp], [w_temp, h_temp], [w_temp, 0]]).reshape(-1, 1, 2)
    dst = cv2.perspectiveTransform(pts, M)

    xmin, ymin = np.int32(dst.min(axis=0).ravel())
    xmax, ymax = np.int32(dst.max(axis=0).ravel())
    center_x, center_y = (xmin + xmax) / 2, (ymin + ymax) / 2
    orig_h, orig_w = img_orig.shape[:2]

    target_w, target_h = 456, 564
    ratio = target_w / target_h # ≈0.8085
    
    final_h = ymax - ymin
    final_w = final_h * ratio
    
    x1 = int(center_x - final_w / 2)
    y1 = int(center_y - final_h / 2)
    x2, y2 = int(x1 + final_w), int(y1 + final_h)

    dx = max(0, -x1) - max(0, x2 - orig_w)
    dy = max(0, -y1) - max(0, y2 - orig_h)
    x1, y1, x2, y2 = x1+dx, y1+dy, x2+dx, y2+dy
    
    x1, y1, x2, y2 = max(0, x1), max(0, y1), min(orig_w, x2), min(orig_h, y2)

    high_res_crop = img_orig[y1:y2, x1:x2]
    
    if high_res_crop.size == 0:
        return False
    cv2.imwrite(output_res_path, high_res_crop)
    fixed_res_img = cv2.resize(high_res_crop, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(output_fixed_path, fixed_res_img)

    return True

def main():
    temp_dir = "templates"
    input_dir = "input_images"
    out_res_dir = "output_high_res"
    out_fixed_dir = "output_fixed_456x564"

    for d in [out_res_dir, out_fixed_dir]:
        if not os.path.exists(d): os.makedirs(d)

    temp_files = glob.glob(os.path.join(temp_dir, "*.png"))
    orig_files = glob.glob(os.path.join(input_dir, "*.png"))

    print(f"开始根据模板批量生成双规格图片...")

    for t_path in temp_files:
        name = os.path.splitext(os.path.basename(t_path))[0]
        matching_orig = [o for o in orig_files if name in os.path.basename(o)]
        
        if not matching_orig:
            print(f"找不到原图: {name}")
            continue
            
        o_path = matching_orig[0]
        res_path = os.path.join(out_res_dir, f"{name}.png")
        fixed_path = os.path.join(out_fixed_dir, f"{name}.png")
        
        print(f" 正在匹配并裁剪: {name}...", end=" ", flush=True)
        
        if process_dual_outputs(o_path, t_path, res_path, fixed_path):
            print("完成")
        else:
            print("失败(匹配点不足)")

if __name__ == "__main__":
    main()