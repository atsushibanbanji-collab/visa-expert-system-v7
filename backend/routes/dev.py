"""
開発用エンドポイント

本番デプロイ時に削除:
1. このファイル (routes/dev.py)
2. main.py の dev router インポートと登録
3. frontend/src/components/DevBuildTag.js
4. frontend/src/App.js の DevBuildTag 関連
5. frontend/src/App.css の .dev-build-tag スタイル
"""
import subprocess
from fastapi import APIRouter

router = APIRouter(prefix="/api/dev", tags=["dev"])


def _get_git_hash() -> str:
    """起動時のGitコミットハッシュを取得"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short=7", "HEAD"],
            capture_output=True,
            text=True,
            cwd=__file__.rsplit("\\", 2)[0]  # backendディレクトリ
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


# サーバー起動時にハッシュを取得（以降変わらない）
_commit_hash = _get_git_hash()


@router.get("/info")
async def get_dev_info():
    """開発用情報を取得"""
    return {"commit_hash": _commit_hash}
