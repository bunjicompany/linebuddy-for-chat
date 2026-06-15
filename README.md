# いつもの改行 for Excel / LineBuddy for Excel

Excelのセル内で、`Alt + Enter` の代わりに `Enter` または `Shift + Enter` でセル内改行できるWindows常駐アプリです。

英語UIでは **LineBuddy for Excel** という名前で表示します。

## 主な特徴

- `Enter` または `Shift + Enter` をセル内改行キーとして選択できます。
- Excelのセル内で文字入力中のときだけ、選択したキーを `Alt + Enter` に変換します。
- セルを選択しているだけの状態、図形・テキストボックス入力中、Excel以外のアプリでは変換しません。
- 日本語入力の変換確定を邪魔しないよう、IMEの状態を見て変換を抑制します。
- タスクトレイに常駐し、一時停止・再開、言語切替、バージョン表示ができます。
- 日本語/英語のUI切替に対応しています。

## 対応環境

- Windows
- Excel 2010
- Excel 2019
- Microsoft 365版Excel

Excelのバージョンや更新状況によって、セル編集中の判定方法が異なるため、一部環境ではうまく動作しない可能性があります。

## 使い方

1. [公式配布ページ](https://bunjicompany.com/downloads/ItsumonoKaigyoForExcel/) または [GitHub Releases](https://github.com/bunjicompany/linebuddy-for-excel/releases) から `ItsumonoKaigyoForExcel.exe` をダウンロードして起動します。
2. 必要に応じて、セル内改行キーを `Enter` または `Shift + Enter` から選びます。
3. Excelのセル内で文字入力中に、選択したキーを押します。
4. 選択したキーが `Alt + Enter` として送信され、セル内改行されます。

## 安全設計

このアプリは、誤変換を避けるために「変換されない」ことを優先しています。

- Excelが前面ではない場合は変換しません。
- セル内入力中だと判断できない場合は変換しません。
- 図形・テキストボックス入力中は変換しません。
- 日本語変換の確定中と判断した場合は、確定を優先して変換しません。
- キー以外の操作でセル編集を抜けた可能性がある場合は、古い推定状態を使わず変換しません。

## 開発環境

アプリ本体は Python と Windows API（ctypes）で実装しています。exe化には PyInstaller を使います。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm ItsumonoKaigyoForExcel.spec
```

または、PowerShellで次を実行します。

```powershell
.\build_exe.ps1
```

ビルドすると、`dist\ItsumonoKaigyoForExcel.exe` が生成されます。ビルド時にアプリ内のバージョン情報も更新されます。

## 主なファイル

- `excel_line_breaker.py`: アプリ本体
- `ItsumonoKaigyoForExcel.spec`: PyInstaller設定
- `app_icon.ico`: アプリアイコン
- `requirements.txt`: 開発・ビルド用依存関係

## リンク

- [公式配布ページ](https://bunjicompany.com/downloads/ItsumonoKaigyoForExcel/)
- [GitHub Releases](https://github.com/bunjicompany/linebuddy-for-excel/releases)

## ライセンス

MIT Licenseです。詳しくは [LICENSE](LICENSE) を参照してください。

## 作者

[ぶんじカンパニー](https://bunjicompany.com/)
