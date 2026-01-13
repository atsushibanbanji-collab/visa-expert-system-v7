/**
 * 開発用ビルド情報タグ
 *
 * 本番環境へのデプロイ時は以下を削除:
 * 1. このファイル (components/DevBuildTag.js)
 * 2. App.js の DevBuildTag インポートと使用箇所
 * 3. App.css の .dev-build-tag 関連スタイル
 * 4. backend/routes/dev.py
 * 5. backend/main.py の dev router インポート
 */
import React, { useState, useEffect } from 'react';
import { API_BASE } from '../config';

function DevBuildTag() {
  const [commitHash, setCommitHash] = useState(null);

  useEffect(() => {
    const fetchBackendInfo = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/dev/info`);
        if (response.ok) {
          const data = await response.json();
          setCommitHash(data.commit_hash);
        }
      } catch (error) {
        setCommitHash('error');
      }
    };
    fetchBackendInfo();
  }, []);

  if (!commitHash) return null;

  return (
    <div className="dev-build-tag">
      BE: {commitHash}
    </div>
  );
}

export default DevBuildTag;
