/**
 * API通信の基盤ユーティリティ
 */
import { API_BASE } from '../config';

/**
 * エラーレスポンスからメッセージを抽出
 */
export function extractErrorMessage(error, defaultMessage = 'エラーが発生しました') {
  if (typeof error?.detail === 'string') {
    return error.detail;
  }
  if (Array.isArray(error?.detail)) {
    // Pydantic validation error format
    return error.detail.map(e => e.msg || JSON.stringify(e)).join(', ');
  }
  return defaultMessage;
}

/**
 * APIリクエストを実行
 */
export async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  const data = await response.json();

  if (!response.ok) {
    const error = new Error(extractErrorMessage(data));
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}

/**
 * GETリクエスト
 */
export function apiGet(endpoint) {
  return apiRequest(endpoint);
}

/**
 * POSTリクエスト
 */
export function apiPost(endpoint, body) {
  return apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/**
 * PUTリクエスト
 */
export function apiPut(endpoint, body) {
  return apiRequest(endpoint, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
}
