import os

def count_files_and_folders(directory_path):
    """
    统计指定文件夹中第一级子文件和子文件夹的数量
    """
    if not os.path.exists(directory_path):
        print(f"Error: Directory {directory_path} does not exist.")
        return 0

    items = os.listdir(directory_path)
    return len(items)

if __name__ == "__main__":
    directory_path = r"C:\Users\sunguyi\Desktop\repos\github_1min_stars_projects"
    total_items = count_files_and_folders(directory_path)
    print(f"Total number of files and folders in {directory_path}: {total_items}")