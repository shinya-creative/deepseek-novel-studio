import os
import re
from datetime import datetime


def get_next_number():
    if not os.path.exists("novels"):
        os.makedirs("novels", exist_ok=True)
        return 0

    # 既存のフォルダ名から「#数字」の部分を探して最大値を求める
    folders = [d for d in os.listdir("novels") if os.path.isdir(f"novels/{d}")]
    max_num = -1
    for folder in folders:
        match = re.match(r"^#(0|[1-9]\d*)", folder)
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
- タグ: #獣人 #学園モノ
- 擬音・擬態語の使用: false
- 参考URL(pixiv小説など):

## 登場人物
- 主人公（種族）
- サブキャラ1
- サブキャラ2...

## 物語の着地点（結末）

## 世界観・シチュエーション
-

## 執筆指示
-
"""

    settings_path = os.path.join(path, "settings.md")
    manuscript_path = os.path.join(path, "manuscript.md")

    with open(settings_path, "w", encoding="utf-8") as settings_file:
        settings_file.write(settings_content)

    if not os.path.exists(manuscript_path):
        with open(manuscript_path, "w", encoding="utf-8") as manuscript_file:
            manuscript_file.write(f"# {title}\n\n")

    print(f"\n作成完了: {path}")
    print(f"settings: {settings_path}")
    print(f"manuscript: {manuscript_path}")


def list_novels():
    if not os.path.exists("novels"):
        print("作品が見つかりません。先に create を実行してください。")
        return

    novels = [d for d in os.listdir("novels") if os.path.isdir(os.path.join("novels", d))]
    novels.sort()

    if not novels:
        print("作品が見つかりません。先に create を実行してください。")
        return

    print("\n執筆可能な作品一覧:")
    for index, name in enumerate(novels):
        print(f"{index}: {name}")

    choice = input("\nどの小説を書きますか？ (番号を入力): ")
    try:
        selected = novels[int(choice)]
    except (ValueError, IndexError):
        print("無効な選択です。")
        return

    print(f"\nSELECTED_NOVEL: {selected}")


def list_versions():
    if not os.path.exists("novels"):
        print("作品が見つかりません。")
        return

    novels = [d for d in os.listdir("novels") if os.path.isdir(os.path.join("novels", d))]
    novels.sort()

    if not novels:
        print("作品が見つかりません。")
        return

    print("\n執筆可能な作品一覧:")
    for index, name in enumerate(novels):
        print(f"{index}: {name}")

    choice = input("\nバージョン一覧を見たい作品は？ (番号を入力): ")
    try:
        selected = novels[int(choice)]
    except (ValueError, IndexError):
        print("無効な選択です。")
        return

    versions_dir = os.path.join("novels", selected, "versions")
    if not os.path.exists(versions_dir):
        print(f"\n'{selected}' にバージョン履歴はありません。")
        return

    versions = sorted(
        [f for f in os.listdir(versions_dir) if re.match(r"^manuscript_v\d+\.md$", f)],
        key=lambda x: int(re.search(r"\d+", x).group())
    )

    if not versions:
        print(f"\n'{selected}' にバージョン履歴はありません。")
        return

    print(f"\n■ '{selected}' のバージョン履歴")
    print(f"  {'Ver':<6} {'保存日時':<22} {'ファイルサイズ'}")
    print(f"  {'-'*6} {'-'*22} {'-'*14}")
    for v in versions:
        vpath = os.path.join(versions_dir, v)
        mtime = datetime.fromtimestamp(os.path.getmtime(vpath)).strftime("%Y-%m-%d %H:%M:%S")
        size = os.path.getsize(vpath)
        print(f"  {v:<30} {mtime}   {size:>10,} bytes")

    current = os.path.join("novels", selected, "manuscript.md")
    if os.path.exists(current):
        mtime = datetime.fromtimestamp(os.path.getmtime(current)).strftime("%Y-%m-%d %H:%M:%S")
        size = os.path.getsize(current)
        print(f"  {'manuscript.md (最新)':<30} {mtime}   {size:>10,} bytes")

    print(f"\n  ファイルの場所: novels/{selected}/versions/")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "start":
        list_novels()
    elif len(sys.argv) > 1 and sys.argv[1] == "versions":
        list_versions()
    else:
        create_novel()