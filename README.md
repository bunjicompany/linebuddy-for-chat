# いつもの改行 for Chat

生成AI、SNS、チャットアプリの入力欄で、Enterキーを入力欄内改行に置き換えるWindows常駐ツールです。

このツールは送信キーそのものの変更や送信操作の代替は行いません。変換するのは、入力欄内改行だけです。

<table>
  <tr>
    <td><img src="assets/dialog-top.png" alt="いつもの改行 for Chat のメイン画面"></td>
    <td><img src="assets/dialog-settings.png" alt="いつもの改行 for Chat の設定画面"></td>
  </tr>
  <tr>
    <td colspan="2"><img src="assets/dialog-edit-custom.png" alt="いつもの改行 for Chat のカスタム編集画面"></td>
  </tr>
</table>

## ダウンロード

一般ユーザー向けの説明・最新版ダウンロードはこちらです。

https://bunjicompany.com/downloads/ItsumonoKaigyoForChat/

過去バージョン・更新履歴はこちらです。

https://github.com/bunjicompany/linebuddy-for-chat/releases

## 安全性について

このアプリは、入力した文章・パスワード・クリップボードの内容を読み取り・保存しません。
キー操作を変換するために必要な範囲で、現在のウィンドウ状態とキー入力イベントを判定します。
外部サーバーへの送信は行いません。

個人開発アプリのため、Windows SmartScreenの警告が表示される場合があります。

## 主な機能

- 生成AI、SNS、チャットの対象ごとにオン/オフを選択できます。
- Web版とApp版を分けて管理できます。
- 日本語IME変換中のEnterは、文字確定を優先します。
- タイトル、URL、プロセス名のキーワードでカスタム対象を追加できます。
- タスクトレイから一時停止、設定、言語切替、Windows起動時登録を操作できます。

## 初期プリセット

### 生成AI

- ChatGPT Web / App
- Codex App
- Claude Web / App
- Gemini Web
- Copilot Web / App
- Perplexity Web
- Grok Web
- DeepSeek Web

### SNS・チャット

- LINE App
- X Web
- Slack Web / App
- Discord Web / App
- Teams Web / App
- Instagram Web
- WhatsApp Web / App

## 開発・ビルド

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm ItsumonoKaigyo.spec
```

または:

```powershell
.\build_exe.ps1
```

ビルド後、`dist\ItsumonoKaigyoForChat.exe` が生成されます。

## 主なファイル

- `itsumono_kaigyo.py`: アプリ本体
- `ItsumonoKaigyo.spec`: PyInstaller設定
- `app_icon.ico`: アプリアイコン
- `ItsumonoKaigyoForChat_settings.json`: 設定ファイル
