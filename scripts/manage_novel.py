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
- ふりがな: false
- 参考URL(小説サイトなど):

## 登場人物
<!-- 名前・種族・性格・立場・関係性を書くと安定します -->
- 主人公（種族）:
- サブキャラ1:

## キャラクター口調
<!-- 各キャラクターのセリフの特徴を書くと、より個性的な会話になります -->
<!-- 例: 登場人物X: 落ち着いた語り口。短文が多い。語尾に「…」をよく使う。 -->
-

## 擬音・効果音ルール
<!-- 「擬音・擬態語の使用: true」の場合に参照されます -->
<!-- 使用する擬音の例（例: ドキドキ、ふわっ、ぎゅっ、とくん）: -->
- 使用する擬音の例:
<!-- 避ける擬音・表現（例: ズドーン、ドカーン などの激しすぎるもの）: -->
- 避ける表現:
- 密度: 少なめ

## 物語の着地点（結末）

## 世界観・シチュエーション
-

## 執筆指示
-
"""

    settings_path = os.path.join(path, "settings.md")
    manuscript_path = os.path.join(path, "manuscript.md")
    reference_path = os.path.join(path, "reference.md")

    with open(settings_path, "w", encoding="utf-8") as settings_file:
        settings_file.write(settings_content)

    if not os.path.exists(manuscript_path):
        with open(manuscript_path, "w", encoding="utf-8") as manuscript_file:
            manuscript_file.write(f"# {title}\n\n")

    reference_template = """# 参考文章（スタイル学習用）

<!-- pixiv など認証が必要なサイトは自動取得できません。 -->
<!-- 参考にしたい作品から気に入った文章をそのままここへ貼り付けてください。 -->
<!-- 貼り付けた文章の文体・テンポ・語彙・リズムが本文生成に反映されます。 -->
<!-- 複数の作品から貼り付けても構いません。不要なら空白のままでOKです。 -->

"""
    with open(reference_path, "w", encoding="utf-8") as ref_file:
        ref_file.write(reference_template)

    print(f"\n作成完了: {path}")
    print(f"settings:  {settings_path}")
    print(f"reference: {reference_path}  ← 参考文章をここへ貼り付けてください")
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