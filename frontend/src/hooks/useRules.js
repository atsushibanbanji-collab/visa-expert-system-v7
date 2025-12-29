/**
 * ルール管理用カスタムフック
 */
import { useState, useCallback } from 'react';
import { apiGet, apiPost, apiPut } from './useApi';

/**
 * ルール一覧の取得・管理
 */
export function useRules() {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRules = useCallback(async (visaType = '', sort = 'none') => {
    setLoading(true);
    setError(null);
    try {
      let endpoint = `/api/rules?sort=${sort}`;
      if (visaType) {
        endpoint += `&visa_type=${visaType}`;
      }
      const data = await apiGet(endpoint);
      setRules(data.rules || []);
      return data.rules;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const createRule = useCallback(async (ruleData) => {
    const data = await apiPost('/api/rules', ruleData);
    return data;
  }, []);

  const updateRule = useCallback(async (ruleData) => {
    const data = await apiPut('/api/rules', ruleData);
    return data;
  }, []);

  const deleteRule = useCallback(async (action) => {
    const data = await apiPost('/api/rules/delete', { action });
    return data;
  }, []);

  const reorderRules = useCallback(async (actions) => {
    const data = await apiPost('/api/rules/reorder', { actions });
    return data;
  }, []);

  const autoOrganize = useCallback(async (mode = 'dependency') => {
    const data = await apiPost('/api/rules/auto-organize', { mode });
    return data;
  }, []);

  return {
    rules,
    loading,
    error,
    fetchRules,
    createRule,
    updateRule,
    deleteRule,
    reorderRules,
    autoOrganize,
    setRules,
  };
}

/**
 * バリデーションチェック
 */
export function useValidation() {
  const [issues, setIssues] = useState([]);
  const [status, setStatus] = useState(null);

  const checkValidation = useCallback(async (visaType = '') => {
    try {
      let endpoint = '/api/validation/check';
      if (visaType) {
        endpoint += `?visa_type=${visaType}`;
      }
      const data = await apiGet(endpoint);
      setStatus(data.status);
      setIssues(data.issues || []);
      return data;
    } catch (err) {
      setStatus('error');
      return { status: 'error', issues: [] };
    }
  }, []);

  return {
    issues,
    status,
    checkValidation,
    hasIssues: issues.length > 0,
  };
}
