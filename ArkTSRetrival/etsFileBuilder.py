import time
import os
import re
import multiprocessing
from typing import Optional, List

from deepseekVisitor import generate_answer
from milvus_import_data import search_similar_images


ROW_PROMPT = ("你是一位专业的ArtTS工程师，结合你所知道的各种要求，我现在要求你给出这个实现这个UI的ArkUI代码，用ArkTS语言编写这段代码，"
              "以下是一段或多端与这个UI相似的UI的ArkTS代码，可以供你参考：")


def create_prompt(description: str, image_path: str) -> str:
    results = search_similar_images(image_path)
    example_str = ''
    for result in results:
        example_str += result['content']
    return description + ROW_PROMPT + example_str


def find_valid_folders(src_dir: str) -> List[int]:
    """预筛选有效文件夹并返回排序后的列表"""
    valid_folders = []

    for folder_name in os.listdir(src_dir):
        folder_path = os.path.join(src_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue

        if not re.fullmatch(r'^\d+$', folder_name):
            continue

        folder_num = int(folder_name)
        required_files = [
            f"{folder_num}.ets",  # 需要生成的目标文件
            f"description{folder_num}.txt",
            f"{folder_num}.jpg"
        ]

        # 检查文件状态
        ets_exists = os.path.exists(os.path.join(folder_path, required_files[0]))
        other_exists = all(
            os.path.exists(os.path.join(folder_path, f))
            for f in required_files[1:]
        )

        if not ets_exists and other_exists:
            valid_folders.append(folder_num)

    return sorted(valid_folders)


def generate_ets_files(
        src_dir: str,
        limit: int,
        api_key: str,
        target_folders: List[int],
        process_idx: int
) -> int:
    success_count = 0
    processed_count = 0

    for folder_num in target_folders:
        if success_count >= limit:
            break

        start_time = time.perf_counter()
        folder_path = os.path.join(src_dir, str(folder_num))
        ets_file = os.path.join(folder_path, f"{folder_num}.ets")
        des_file = os.path.join(folder_path, f"description{folder_num}.txt")
        image_path = os.path.join(folder_path, f"{folder_num}.jpg")

        if os.path.exists(ets_file):
            print(f"[进程{process_idx}] 跳过 {folder_num}.ets (已存在)")
            processed_count += 1
            continue

        try:
            with open(des_file, 'r') as f:
                description = f.read()

            prompt = create_prompt(description, image_path)
            response = generate_answer(api_key, prompt)

            if not response:
                raise ValueError("生成内容为空")

            tmp_path = ets_file + f".{process_idx}.tmp"
            with open(tmp_path, 'w', encoding='utf-8') as f:
                f.write(response)
            os.rename(tmp_path, ets_file)

            elapsed = time.perf_counter() - start_time
            success_count += 1
            processed_count += 1
            print(f"[进程{process_idx}] 成功生成 {folder_num}.ets | 耗时 {elapsed:.3f}s (累计成功：{success_count})")

        except Exception as e:
            elapsed = time.perf_counter() - start_time
            print(f"[进程{process_idx}] 处理 {folder_num} 失败 | 耗时 {elapsed:.3f}s：{str(e)}")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    print(f"[进程{process_idx}] 任务完成：处理 {processed_count} 个，成功 {success_count} 个")
    return success_count


def worker(args):
    src_dir, limit, api_key, folders, idx = args
    return generate_ets_files(src_dir, limit, api_key, folders, idx)


def main():
    SRC_DIR = '/Users/jiaoyiyang/harmonyProject/repos/combined'
    API_KEYS = ["sk-9af18059f9d548cea65ca2d5fa0fb28a"]
    TOTAL_LIMIT = 1500

    # 预筛选有效文件夹
    valid_folders = find_valid_folders(SRC_DIR)
    print(f"找到 {len(valid_folders)} 个需要处理的文件夹")

    if not valid_folders:
        print("没有需要处理的文件夹")
        return

    # 计算分配策略
    num_processes = len(API_KEYS)
    chunk_size = len(valid_folders) // num_processes
    remainder = len(valid_folders) % num_processes

    # 创建任务块
    chunks = []
    start = 0
    for i in range(num_processes):
        end = start + chunk_size + (1 if i < remainder else 0)
        chunks.append(valid_folders[start:end])
        start = end

    # 准备进程参数
    process_args = []
    for idx, chunk in enumerate(chunks):
        per_process_limit = min(TOTAL_LIMIT // num_processes, len(chunk))
        process_args.append((
            SRC_DIR,
            per_process_limit,
            API_KEYS[idx],
            chunk,
            idx + 1
        ))

    # 启动进程池
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(worker, process_args)

    total_success = sum(results)
    print(f"\n总处理结果：{total_success}/{min(TOTAL_LIMIT, len(valid_folders))}")


if __name__ == "__main__":
    main()


