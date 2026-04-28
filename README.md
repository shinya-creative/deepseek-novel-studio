# AI Novel Studio: DeepSeek & Cline 執筆自動化ツール

このツールは、VS Code 拡張機能の **Cline** と **DeepSeek-V4-Flash API** を活用して、詳細な心理描写を持つ短編小説を自動生成するための執筆支援システムです。

## ⚠️ 免責事項・利用規約（必ずお読みください）

1.  **個人利用限定**: 本ツールはあくまで個人が娯楽目的でAIとの創作を楽しむためのものです。
2.  **公開・収益化の禁止**: 本ツールを用いて生成したコンテンツを、小説投稿サイト、SNS、その他グローバルなプラットフォームへ公開すること、および有料販売等の収益化に利用することは固く禁止します。
3.  **自己責任**: 本ツールの利用（API料金の発生、生成内容、実行結果等）に関して、開発者は一切の責任を負いません。すべて利用者の自己責任において使用してください。

---

## 🛠 セットアップ手順

### 1. 必要なソフトウェアのインストール
- **VS Code (Visual Studio Code)**: [公式サイト](https://code.visualstudio.com/)からインストール。
- **Python**: [公式サイト](https://www.python.org/)から 3.10 以上をインストール。
- **重要**: インストール画面で「Add Python to PATH」に必ずチェックを入れてください。

### 2. VS Code 拡張機能の導入
VS Code の拡張機能メニュー（Ctrl+Shift+X）から以下をインストールします。
- **Cline** (旧 Claude Dev)
- **Python** (Microsoft公式)

### 3. プロジェクト環境の構築（仮想環境）
プロジェクトフォルダを VS Code で開き、ターミナル（Ctrl+J）で以下のコマンドを順番に実行して、独立した実行環境（仮想環境）を作成・有効化します。

**Windowsの場合:**
```bash
# 仮想環境の作成
python -m venv .venv
# 仮想環境の有効化
.venv\Scripts\activate
```

**Mac/Linuxの場合:**
```bash
# 仮想環境の作成
python3 -m venv .venv
# 仮想環境の有効化
source .venv/bin/activate
```
※ターミナルの先頭に (.venv) と表示されれば成功です。

### 4. ライブラリのインストール
仮想環境が有効な状態（先頭に (.venv) がある状態）で、必要なライブラリを一括インストールします。

```bash
pip install openai python-dotenv
```

### 5. APIキーとセキュリティ設定
1. DeepSeek Platform でAPIキーを発行します。
2. プロジェクトのルートフォルダに .env という名前のファイルを作成し、以下を書き込みます。

```plaintext
DEEPSEEK_API_KEY=あなたのAPIキー(sk-...)
```

### 6. Cline の初期設定
1. VS Code の左サイドバーから Cline を開きます。
2. 設定（歯車アイコン）をクリックし、以下を入力します。
  - API Provider: DeepSeek
  - API Key: あなたのAPIキー
  - Model: deepseek-chat (最新のFlashモデルが適用されます)
3. プロジェクトのルートにある .clinerules を読み込ませるため、一度チャットで「ルールを確認して」と指示してください。

---

## 🚀 使い方

### コマンド操作（Clineのチャット欄で入力）

- **`create`**:
  - 新規プロジェクト作成。
  - ターミナルでタイトルを入力すると、`novels/#番号 タイトル` フォルダと設定ファイルが生成されます。
- **`start`**:
  - 執筆開始。
  - 作品を選択すると、Clineが自動的に `settings.md` を読み込んで執筆を開始します。

---

## 📁 ディレクトリ構造
- `.clinerules`: Cline への命令定義
- `.env`: APIキー保存用（**公開厳禁**）
- `.gitignore`: 機密ファイル等の除外設定
- `scripts/`: 管理スクリプトおよび執筆エンジン
- `novels/`: 生成された小説の保存先