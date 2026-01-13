import React, { createContext, useContext, useState, useEffect } from 'react';
import { API_BASE } from '../config';

const VisaTypeContext = createContext();

export function VisaTypeProvider({ children }) {
  const [visaTypes, setVisaTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchVisaTypes = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/visa-types`);
      if (response.ok) {
        const data = await response.json();
        setVisaTypes(data.visa_types || []);
        setError(null);
      } else {
        setError('ビザタイプの取得に失敗しました');
      }
    } catch (err) {
      setError('サーバーに接続できません');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVisaTypes();
  }, []);

  // ビザタイプコードのリストを取得
  const getVisaTypeCodes = () => visaTypes.map(v => v.code);

  // リロード関数（管理画面で追加/削除後に呼び出す）
  const reloadVisaTypes = () => {
    setLoading(true);
    fetchVisaTypes();
  };

  return (
    <VisaTypeContext.Provider value={{
      visaTypes,
      visaTypeCodes: getVisaTypeCodes(),
      loading,
      error,
      reloadVisaTypes
    }}>
      {children}
    </VisaTypeContext.Provider>
  );
}

export function useVisaTypes() {
  const context = useContext(VisaTypeContext);
  if (!context) {
    throw new Error('useVisaTypes must be used within a VisaTypeProvider');
  }
  return context;
}
