# ビザ選定エキスパートシステム v7

オブジェクト指向設計によるビザ選定支援Webシステムです。
Smalltalk資料のアーキテクチャに基づき、バックワードチェイニング（後向き推論）方式で実装されています。

## v7 改善点

### 1. OR条件の最適化
- ORルールで1つの条件がTRUEになった場合、同じルールの他の条件の質問をスキップ
- `hypotheses`（推論結果）を`findings`（ユーザー回答）より優先してチェック
- 例: Eビザで「投資=YES」の場合、貿易関連の質問をスキップ

### 2. ブロックルールの伝播
- 親ルールがブロック（FALSE）された場合、子条件の質問をスキップ
- 例: E008（マネージャー能力）がブロック → E009の条件は質問不要

### 3. 推論の最適化
- `_is_ancestor_condition_resolved`メソッドで、TRUEだけでなくFALSEも伝播
- 不要な質問を大幅に削減

### 4. UI改善
- 診断結果の表示改善（ビザ名が縦書きになる問題を修正）
- ボタン連打対策の追加

## システム概要

- **対応ビザタイプ**: E、L、B、H-1B、J-1
- **推論方式**: バックワードチェイニング（ゴールから逆算）
- **特徴**:
  - 全ビザタイプを同時診断
  - 推論過程のリアルタイム可視化
  - 「わからない」回答オプション対応
  - 前の質問に戻る機能

## ローカル起動方法

### 必要環境
- Python 3.8以上
- Node.js 16以上

### 起動手順

1. **バックエンドを起動**
   ```
   start-backend.bat をダブルクリック
   ```
   または
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```

2. **フロントエンドを起動**（別のターミナルで）
   ```
   start-frontend.bat をダブルクリック
   ```
   または
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. ブラウザで http://localhost:3000 にアクセス

## アーキテクチャ

### バックエンド (FastAPI)

```
backend/
├── main.py              # APIエンドポイント
├── inference_engine.py  # 推論エンジン（Consultationクラス相当）
├── knowledge_base.py    # 知識ベース（Ruleクラス相当）
├── models.py            # データモデル
└── requirements.txt     # 依存パッケージ
```

### フロントエンド (React)

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── App.js          # メインコンポーネント
│   ├── App.css         # スタイル
│   └── index.js        # エントリーポイント
└── package.json
```

## API エンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| POST | /api/consultation/start | 診断開始 |
| POST | /api/consultation/answer | 質問に回答 |
| POST | /api/consultation/back | 前の質問に戻る |
| POST | /api/consultation/restart | 最初からやり直し |
| GET | /api/consultation/state/{session_id} | 現在の状態取得 |
| GET | /api/rules | ルール一覧取得 |
| GET | /api/visa-types | ビザタイプ一覧取得 |
| GET | /api/validation/check | ルール整合性チェック |

## デプロイ（Render）

### バックエンド
1. GitHubにpush
2. Renderで新しいWeb Serviceを作成
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### フロントエンド
1. 環境変数 `REACT_APP_API_URL` にバックエンドURLを設定
2. Renderで新しいStatic Siteを作成
3. Build Command: `npm install && npm run build`
4. Publish Directory: `build`
