/**
 * 診断機能用カスタムフック
 */
import { useState, useCallback } from 'react';
import { apiPost, apiGet } from './useApi';

/**
 * 診断セッション管理
 */
export function useConsultation(sessionId) {
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [relatedVisaTypes, setRelatedVisaTypes] = useState([]);
  const [rulesStatus, setRulesStatus] = useState([]);
  const [derivedFacts, setDerivedFacts] = useState([]);
  const [isComplete, setIsComplete] = useState(false);
  const [diagnosisResult, setDiagnosisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const startConsultation = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiPost('/api/consultation/start', { session_id: sessionId });
      setCurrentQuestion(data.current_question);
      setRelatedVisaTypes(data.related_visa_types || []);
      setRulesStatus(data.rules_status || []);
      setIsComplete(data.is_complete);
      return data;
    } catch (err) {
      setError({
        message: err.data?.detail?.error || err.message,
        issues: err.data?.detail?.issues || [],
      });
      return null;
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const answerQuestion = useCallback(async (answer) => {
    setLoading(true);
    try {
      const data = await apiPost('/api/consultation/answer', {
        session_id: sessionId,
        answer,
      });
      setCurrentQuestion(data.current_question);
      setRelatedVisaTypes(data.related_visa_types || []);
      setRulesStatus(data.rules_status || []);
      setDerivedFacts(data.derived_facts || []);
      setIsComplete(data.is_complete);
      if (data.is_complete && data.diagnosis_result) {
        setDiagnosisResult(data.diagnosis_result);
      }
      return data;
    } catch (err) {
      console.error('Error answering question:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const goBack = useCallback(async (steps = 1) => {
    setLoading(true);
    try {
      const data = await apiPost('/api/consultation/back', {
        session_id: sessionId,
        steps,
      });
      setCurrentQuestion(data.current_question);
      setRelatedVisaTypes(data.related_visa_types || []);
      setRulesStatus(data.rules_status || []);
      setIsComplete(false);
      setDiagnosisResult(null);
      return data;
    } catch (err) {
      console.error('Error going back:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const restart = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiPost('/api/consultation/restart', { session_id: sessionId });
      setCurrentQuestion(data.current_question);
      setRelatedVisaTypes(data.related_visa_types || []);
      setRulesStatus(data.rules_status || []);
      setDerivedFacts([]);
      setIsComplete(false);
      setDiagnosisResult(null);
      setError(null);
      return data;
    } catch (err) {
      console.error('Error restarting:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const getState = useCallback(async () => {
    try {
      const data = await apiGet(`/api/consultation/state/${sessionId}`);
      setCurrentQuestion(data.current_question);
      setRelatedVisaTypes(data.related_visa_types || []);
      setRulesStatus(data.rules_status || []);
      setDerivedFacts(data.derived_facts || []);
      setIsComplete(data.is_complete);
      if (data.diagnosis_result) {
        setDiagnosisResult(data.diagnosis_result);
      }
      return data;
    } catch (err) {
      console.error('Error getting state:', err);
      return null;
    }
  }, [sessionId]);

  return {
    currentQuestion,
    relatedVisaTypes,
    rulesStatus,
    derivedFacts,
    isComplete,
    diagnosisResult,
    loading,
    error,
    startConsultation,
    answerQuestion,
    goBack,
    restart,
    getState,
  };
}
