"""
视觉特征提取器
从图片中提取色彩、纹理、构图等审美特征
"""
import cv2
import numpy as np
from collections import Counter

def extract_color_features(img):
    """提取色彩DNA"""
    # 转换色彩空间
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    pixels = rgb.reshape(-1, 3).astype(float)
    hsv_pixels = hsv.reshape(-1, 3).astype(float)

    # 主色调 - 用K-means聚类
    dominant = get_dominant_colors(rgb, k=5)

    # 色温 (warm vs cool)
    r_mean = np.mean(pixels[:, 0])
    b_mean = np.mean(pixels[:, 2])
    warmth = float(np.clip((r_mean - b_mean + 128) / 256 * 100, 0, 100))

    # 饱和度
    saturation = float(np.clip(np.mean(hsv_pixels[:, 1]) / 255 * 100, 0, 100))

    # 明度
    luminosity = float(np.clip(np.mean(hsv_pixels[:, 2]) / 255 * 100, 0, 100))

    # 对比度
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    contrast = float(np.clip(np.std(gray) / 128 * 100, 0, 100))

    # 色彩丰富度
    quantized = (hsv_pixels[:, 0] / 18).astype(int)
    unique_hues = len(set(quantized))
    richness = float(np.clip(unique_hues / 10 * 100, 0, 100))

    return {
        "warmth": round(warmth, 1),
        "saturation": round(saturation, 1),
        "luminosity": round(luminosity, 1),
        "contrast": round(contrast, 1),
        "richness": round(richness, 1),
        "dominant_colors": dominant,
        "hue_hist": get_hue_histogram(hsv_pixels)
    }

def extract_texture_features(img):
    """提取纹理DNA"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 粗糙度 - Laplacian方差
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    roughness = float(np.clip(np.var(laplacian) / 500 * 100, 0, 100))

    # 纹理密度 - 边缘密度
    edges = cv2.Canny(gray, 50, 150)
    edge_density = float(np.clip(np.mean(edges) / 50 * 100, 0, 100))

    # 方向性 - 用Sobel梯度分析
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    angles = np.arctan2(gy, gx) * 180 / np.pi
    hist, _ = np.histogram(angles[edges > 0], bins=36, range=(-180, 180))
    # 方向集中度 = 最大方向占比
    directionality = float(np.clip(np.max(hist) / (np.sum(hist) + 1e-6) * 300, 0, 100))

    # 规则性 - 用自相关分析
    h, w = gray.shape
    small = cv2.resize(gray, (64, 64))
    fft = np.fft.fft2(small.astype(float))
    spectrum = np.abs(np.fft.fftshift(fft))
    regularity = float(np.clip(np.std(spectrum) / np.mean(spectrum) * 20, 0, 100))

    return {
        "roughness": round(roughness, 1),
        "edge_density": round(edge_density, 1),
        "directionality": round(directionality, 1),
        "regularity": round(regularity, 1)
    }

def extract_composition_features(img):
    """提取构图DNA"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # 对称性 - 左右对比
    left = gray[:, :w//2]
    right = np.flip(gray[:, w//2:w//2*2], axis=1)
    min_w = min(left.shape[1], right.shape[1])
    left = left[:, :min_w]
    right = right[:, :min_w]
    symmetry = float(np.clip((1 - np.mean(np.abs(left.astype(float) - right.astype(float))) / 128) * 100, 0, 100))

    # 疏密比 - 暗区vs亮区
    dark_ratio = np.mean(gray < 80)
    light_ratio = np.mean(gray > 175)
    density_ratio = float(np.clip((1 - abs(dark_ratio - light_ratio)) * 100, 0, 100))

    # 视觉重心偏移
    moments = cv2.moments(gray)
    if moments['m00'] > 0:
        cx = moments['m10'] / moments['m00']
        cy = moments['m01'] / moments['m00']
        offset_x = abs(cx - w/2) / (w/2) * 100
        offset_y = abs(cy - h/2) / (h/2) * 100
        balance = float(np.clip(100 - (offset_x + offset_y) / 2, 0, 100))
    else:
        balance = 50.0

    # 复杂度 - 区域数量
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    complexity = float(np.clip(len(contours) / 50 * 100, 0, 100))

    return {
        "symmetry": round(symmetry, 1),
        "density_balance": round(density_ratio, 1),
        "visual_balance": round(balance, 1),
        "complexity": round(complexity, 1)
    }

def get_dominant_colors(rgb, k=5):
    """K-means提取主色"""
    pixels = rgb.reshape(-1, 3).astype(np.float32)
    # 采样加速
    indices = np.random.choice(len(pixels), min(5000, len(pixels)), replace=False)
    sample = pixels[indices]
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, labels, centers = cv2.kmeans(sample, k, None, criteria, 3, cv2.KMEANS_PP_CENTERS)
    # 计算每种颜色占比
    counts = Counter(labels.flatten())
    total = sum(counts.values())
    colors = []
    for i, center in enumerate(centers):
        r, g, b = int(center[0]), int(center[1]), int(center[2])
        ratio = counts.get(i, 0) / total
        colors.append({
            "rgb": [r, g, b],
            "hex": f"#{r:02x}{g:02x}{b:02x}",
            "ratio": round(ratio, 3)
        })
    colors.sort(key=lambda c: c["ratio"], reverse=True)
    return colors

def get_hue_histogram(hsv_pixels, bins=12):
    """色相直方图"""
    hues = hsv_pixels[:, 0]
    hist, _ = np.histogram(hues, bins=bins, range=(0, 180))
    total = np.sum(hist)
    if total > 0:
        hist = hist / total
    return [round(float(h), 3) for h in hist]

def extract_all(img_path):
    """提取全部特征"""
    img = cv2.imread(img_path)
    if img is None:
        return None

    color = extract_color_features(img)
    texture = extract_texture_features(img)
    composition = extract_composition_features(img)

    return {
        "color": color,
        "texture": texture,
        "composition": composition,
        "image_size": {"width": img.shape[1], "height": img.shape[0]}
    }

def features_to_aesthetic_dna(features):
    """将CV特征映射到8维审美DNA（供基因编辑器使用）"""
    if not features:
        return {k: 50 for k in [
            "color_warmth","saturation","pattern_complex","texture_feel",
            "style_modern","material_weight","luminosity","organic_ratio"
        ]}

    c = features.get("color", {})
    t = features.get("texture", {})
    p = features.get("composition", {})

    return {
        "color_warmth":    round(c.get("warmth", 50)),
        "saturation":      round(c.get("saturation", 50)),
        "pattern_complex": round(p.get("complexity", 50)),
        "texture_feel":    round(t.get("roughness", 50)),
        "style_modern":    round(max(0, min(100, 100 - p.get("symmetry", 50) * 0.5 - t.get("regularity", 50) * 0.3))),
        "material_weight": round(t.get("edge_density", 50)),
        "luminosity":      round(c.get("luminosity", 50)),
        "organic_ratio":   round(max(0, min(100, t.get("directionality", 50) * 0.6 + (100 - t.get("regularity", 50)) * 0.4)))
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = extract_all(sys.argv[1])
        if result:
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
            dna = features_to_aesthetic_dna(result)
            print("\nAesthetic DNA:")
            print(json.dumps(dna, indent=2))