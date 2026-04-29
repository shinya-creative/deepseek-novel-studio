import html as html_module
import os
import re
import shutil
import sys
import urllib.request
from datetime import datetime
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

def backup_manuscript(folder_name):
    """上書き前に manuscript.md を versions/ フォルダへバックアップする。"""
    manuscript_path = f"novels/{folder_name}/manuscript.md"
    if not os.path.exists(manuscript_path):
        return

    with open(manuscript_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    if not content:
        return

    versions_dir = f"novels/{folder_name}/versions"
    os.makedirs(versions_dir, exist_ok=True)

    existing = [
        f for f in os.listdir(versions_dir)
        if re.match(r"^manuscript_v\d+\.md$", f)
    ]
    next_version = len(existing) + 1

    backup_path = os.path.join(versions_dir, f"manuscript_v{next_version}.md")
    shutil.copy2(manuscript_path, backup_path)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[バックアップ] v{next_version} を保存しました ({timestamp})")
    print(f"             保存先: {backup_path}")


def fetch_reference_text(url, max_chars=2000):
    """参考URLからテキストを取得する（ベストエフォート）。取得できない場合は空文字を返す。"""
    if not url:
        return ""
    url = url.strip()
    if not url.startswith("http"):
        return ""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", raw, flags=re.DOTALL | re.IGNORECASE)
        raw = re.sub(r"<[^>]+>", "", raw)
        raw = html_module.unescape(raw)
        lines = [ln.strip() for ln in raw.splitlines() if len(ln.strip()) > 10]
        text = "\n".join(lines)
        if len(text) < 300:
            return ""
        return text[:max_chars]
    except Exception:
        return ""


def extract_reference_url(settings):
    """settings.md から参考URLを抽出する。"""
    match = re.search(r"参考URL[^\n:：]*[:：]\s*(https?://\S+)", settings)
    return match.group(1).strip() if match else ""


def load_reference_file(folder_name):
    """reference.mdの実質本文を返す。テンプレートのみなら空文字を返す。"""
    path = f"novels/{folder_name}/reference.md"
    if not os.path.exists(path):
        return ""

    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    # テンプレートのコメント行を除外
    content = re.sub(r"<!--.*?-->", "", raw, flags=re.DOTALL)

    # セクション見出しのみの行（# 参考文章 など）を除外
    meaningful_lines = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        meaningful_lines.append(stripped)

    normalized = "\n".join(meaningful_lines).strip()
    return normalized


def build_system_prompt(settings, has_reference=False):
    """settings.md の内容を解析して動的なシステムプロンプトを構築する。"""
    base = (
        "あなたはプロの小説家です。提供された設定を厳守し、"
        "情景描写や心理描写を極めて詳細に（1エピソード2万文字程度の密度を目標に）"
        "日本語で執筆してください。"
    )
    rules = []

    if "## キャラクター口調" in settings:
        rules.append(
            "【キャラクター口調】セクションに記載された各キャラクターの話し方・語尾・口癖を必ず守り、"
            "キャラクターごとに個性的なセリフを書くこと。"
        )

    if "擬音・擬態語の使用: true" in settings:
        if "## 擬音・効果音ルール" in settings:
            rules.append(
                "【擬音・効果音ルール】セクションの指示に従い、指定の擬音を積極的に使用し、"
                "避けるべき表現は一切使わないこと。"
            )
        else:
            rules.append("擬音・擬態語を積極的に使い、場面の勢いやキャラクターの感情を表現すること。")
    else:
        rules.append(
            "擬音・擬態語は使用せず、心理描写・情景描写・身体感覚の描写で感情や動作を表現すること。"
        )

    if has_reference:
        rules.append(
            "【参考文章】として提供されたサンプルの文体・テンポ・語彙・文章リズムを"
            "徹底的に分析し、本文全体に反映すること。"
        )

    if "ふりがな: true" in settings:
        rules.append(
            "文化庁『常用漢字表』（平成22年内閣告示・2136字）を基準に、"
            "①表外漢字（常用漢字表にない漢字）、"
            "②表内漢字でも一般的でない読み方・難読な読み、"
            "③人名・地名などの固有名詞（初出時のみ）"
            "に対して 漢字(ふりがな) の形式でふりがなを付けること。"
            "常用漢字の一般的な読み方にはふりがなを付けないこと。"
        )

    prompt = base
    if rules:
        prompt += "\n\n【執筆ルール（厳守）】\n" + "\n".join(f"- {r}" for r in rules)
    return prompt


def generate_novel(folder_name):
    configure_console_output()
    path = f"novels/{folder_name}/settings.md"

    # 2. settings.md の読み込み
    if not os.path.exists(path):
        print(f"エラー: {path} が見つかりません。")
        return

    with open(path, "r", encoding="utf-8") as f:
        settings = f.read()

    # 1. reference.md の読み込み（優先）
    ref_path = f"novels/{folder_name}/reference.md"
    ref_text = load_reference_file(folder_name)
    if ref_text:
        print(f"[参考文章] reference.md を読み込みました（{len(ref_text)} 文字）。文体学習に使用します。")
    else:
        if os.path.exists(ref_path):
            print("[参考文章] reference.md に有効な追記がないためスキップします。")
        # 2. reference.md がなければ参考URLからテキスト取得を試みる
        ref_url = extract_reference_url(settings)
        if ref_url:
            print(f"[参考URL] テキスト取得を試みます: {ref_url}")
            ref_text = fetch_reference_text(ref_url)
            if ref_text:
                print(f"[参考URL] {len(ref_text)} 文字取得しました。文体学習に使用します。")
            else:
                print("[参考URL] 自動取得できませんでした。reference.md への貼り付けをお試しください。")

    print(f"--- '{folder_name}' の執筆を開始します ---")

    # システムプロンプトの動的構築
    system_prompt = build_system_prompt(settings, has_reference=bool(ref_text))

    # ユーザーメッセージの構築（参考テキストがあれば付加）
    user_message = f"以下の設定に基づいて、小説の第1章を執筆してください。\n\n{settings}"
    if ref_text:
        user_message += f"\n\n---\n【参考文章（文体・スタイル学習用）】\n{ref_text}"

    # 3. DeepSeekへのリクエスト
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.8,
        stream=True
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

    # 5. ファイルに保存（上書き前に旧バージョンをバックアップ）
    output_path = f"novels/{folder_name}/manuscript.md"
    backup_manuscript(folder_name)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_content)

    print(f"\n\n[完了] 執筆が完了しました！ 保存先: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        folder = " ".join(sys.argv[1:]).strip()
        generate_novel(folder)
    else:
        print("使い方: python scripts/generator.py \"#番号 タイトル\"")