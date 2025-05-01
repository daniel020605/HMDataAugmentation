import cv2
import numpy as np

# 像素级比较（MSE）
def compare_mse(img1, img2):
    # 确保图片尺寸相同
    img1 = cv2.resize(img1, (img2.shape[1], img2.shape[0]))
    err = np.sum((img1.astype("float") - img2.astype("float")) ** 2)
    err /= float(img1.shape[0] * img1.shape[1] * img1.shape[2])

    # 值越小，越相似
    return err

# 感知哈希比较
def dhash(image, hash_size=8):
    # 调整图像大小
    resized = cv2.resize(image, (hash_size + 1, hash_size))
    # 计算水平差异
    diff = resized[:, 1:] > resized[:, :-1]
    # 转换为哈希值
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])

def compare_hash(img1, img2):
    hash1 = dhash(img1)
    hash2 = dhash(img2)
    # 计算汉明距离
    return bin(hash1 ^ hash2).count('1')

# 直方图比较
def compare_histogram(img1, img2):
    # 转换为HSV色彩空间
    hsv1 = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)
    hsv2 = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)

    # 计算直方图
    h_bins = 50
    s_bins = 60
    hist_size = [h_bins, s_bins]
    ranges = [0, 180, 0, 256]

    hist1 = cv2.calcHist([hsv1], [0, 1], None, hist_size, ranges)
    hist2 = cv2.calcHist([hsv2], [0, 1], None, hist_size, ranges)

    # 归一化
    cv2.normalize(hist1, hist1, 0, 1, cv2.NORM_MINMAX)
    cv2.normalize(hist2, hist2, 0, 1, cv2.NORM_MINMAX)

    # 比较直方图（值越大，越相似）
    return cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

# 特征点匹配
def compare_sift(img1, img2):
    # 创建SIFT检测器
    sift = cv2.SIFT_create()

    # 检测关键点和描述符
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)

    # FLANN匹配
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    matches = flann.knnMatch(des1, des2, k=2)

    # Lowe's比率测试
    good_matches = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)

    # 匹配点数量越多，相似度越高
    return len(good_matches) / min(len(kp1), len(kp2))

import torch
from torchvision import models, transforms

# 深度学习特征提取
def extract_features(img, model):
    # 预处理
    preprocess = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    img_tensor = preprocess(img).unsqueeze(0)

    # 特征提取
    with torch.no_grad():
        features = model(img_tensor)

    return features.numpy().flatten()

def compare_deep_features(img1, img2):
    # 加载预训练模型
    model = models.resnet18(pretrained=True)
    # 移除分类层
    model = torch.nn.Sequential(*(list(model.children())[:-1]))
    model.eval()

    # 提取特征
    feat1 = extract_features(img1, model)
    feat2 = extract_features(img2, model)

    # 计算余弦相似度
    similarity = np.dot(feat1, feat2) / (np.linalg.norm(feat1) * np.linalg.norm(feat2))
    return similarity


def compare_pipe(img1, img2):
    # 比较图片
    mse = compare_mse(img1, img2)
    dhash_diff = compare_hash(img1, img2)
    hist_diff = compare_histogram(img1, img2)
    sift_diff = compare_sift(img1, img2)
    deep_diff = compare_deep_features(img1, img2)

    print(f'MSE: {mse}')
    print(f'DHash Difference: {dhash_diff}')
    print(f'Histogram Correlation: {hist_diff}')
    print(f'SIFT Similarity: {sift_diff}')
    print(f'Deep Feature Similarity: {deep_diff}')

    print("-------------------------------")

if __name__ == '__main__':
    # 读取图片
    img1 = cv2.imread('/Users/liuxuejin/Desktop/images/1.png')
    img2 = cv2.imread('/Users/liuxuejin/Desktop/images/2.png')
    img3 = cv2.imread('/Users/liuxuejin/Desktop/images/3.png')
    img4 = cv2.imread('/Users/liuxuejin/Desktop/images/4.png')
    img74_1 = cv2.imread('/Users/liuxuejin/Desktop/images/74.png')
    img74_2 = cv2.imread('/Users/liuxuejin/Desktop/images/74.jpg')
    compare_pipe(img1, img2)
    compare_pipe(img1, img3)
    compare_pipe(img1, img4)
    compare_pipe(img2, img3)
    compare_pipe(img2, img4)
    compare_pipe(img3, img4)
    compare_pipe(img74_2, img74_1)
    img334_1 = cv2.imread('/Users/liuxuejin/Desktop/images/334.png')
    img334_2 = cv2.imread('/Users/liuxuejin/Desktop/images/334.jpg')
    compare_pipe(img334_1, img334_2)