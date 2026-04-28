import os
import re

def get_next_number():
    if not os.path.exists("novels"):
        os.makedirs("novels", exist_ok=True)
        return 0

    # 既存のフォルダ名から「#数字」の部分を探して最大値を求める
    folders = [d for d in os.listdir("novels") if os.path.isdir(f"novels/{d}")]
    max_num = -1
    for folder in folders:
        match = re.match(r"^#(\0|([1-9]\d*))", folder)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    return max_num + 1

def create_novel():
    title = input("小説のタイトルを入力してください: ")
    next_num = get_next_number()

    # フォルダ名を「#番号 タイトル」の形式にする
    folder_name = f"#{next_num} {title}"
    path = f"novels/{folder_name}"
    os.makedirs(path, exist_ok=True)

    settings_content = f"""# 設定: {title}

## 基本情報
- タイトル: {title}
- 形式: 一章完結（短編）
- 管理番号: {next_num}
- タグ: #獣人 #BL #学園モノ
- 擬音・擬態語の使用: false
- 参考URL(pixiv小説など):

## 登場人物
- 主人公（獣人）
- サブキャラ1
- サブキャラ2...

## 物語の着地点（結末）

## 世界観・シチュエーション
-

## 執筆指示
-
"""