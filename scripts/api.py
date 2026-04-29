import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# 環境変数からキーを取得
api_key = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)


def configure_console_output():
    if os.name == "nt":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleOutputCP(65001)
            kernel32.SetConsoleCP(65001)
        except Exception:
            pass

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

def generate_novel(folder_name):
    configure_console_output()
    path = f"novels/{folder_name}/settings.md"

    # 2. settings.md の読み込み
    if not os.path.exists(path):
        print(f"エラー: {path} が見つかりません。")
        return

    with open(path, "r", encoding="utf-8") as f:
        settings = f.read()

    print(f"--- '{folder_name}' の執筆を開始します ---")

    # 3. DeepSeekへのリクエスト
    # .clinerulesで定義した「2万文字」などの意図をシステムプロンプトに反映
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {
                "role": "system",
                "content": "あなたはプロの小説家です。提供された設定を厳守し、情景描写や心理描写を極めて詳細に（1エピソード2万文字程度の密度を目標に）日本語で執筆してください。"
            },
            {
                "role": "user",
                "content": f"以下の設定に基づいて、小説の第1章を執筆してください。\n\n{settings}"
            }
        ],
        temperature=0.8, # 小説らしい揺らぎを持たせる
        stream=True     # 執筆風景が見えるようにストリーミング推奨
    )

    # 4. 結果の出力と保存
    full_content = ""
    print("\n[本文生成中...]\n")
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            sys.stdout.write(content)
            sys.stdout.flush()
            full_content += content

    # 5. ファイルに保存
    output_path = f"novels/{folder_name}/manuscript.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_content)

    print(f"\n\n[完了] 執筆が完了しました！ 保存先: {output_path}")

# テスト実行用（Cline経由ではなく直接動かす場合、ここにフォルダ名を入れる）
if __name__ == "__main__":
    # 実際には管理スクリプトから渡された名前を使うか、手動で指定
    # generate_novel("#0 タイトル")
    pass