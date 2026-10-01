import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';
interface CaseState { caseId: string | null; jobId: string | null }
interface CaseContextValue extends CaseState { setCase: (caseId: string, jobId?: string | null) => void; reset: () => void }
const key = 'cerebraq.active-case';
const initial = (): CaseState => {
  try {
    const raw = sessionStorage.getItem(key);
    if (raw) { const parsed: unknown = JSON.parse(raw); if (typeof parsed === 'object' && parsed !== null && 'caseId' in parsed && typeof parsed.caseId === 'string' && parsed.caseId.length < 128 && (!('jobId' in parsed) || parsed.jobId === null || typeof parsed.jobId === 'string')) return { caseId: parsed.caseId, jobId: 'jobId' in parsed && typeof parsed.jobId === 'string' ? parsed.jobId : null }; }
  } catch { /* storage may be disabled */ }
  return { caseId: null, jobId: null };
};
const CaseContext = createContext<CaseContextValue | null>(null);
export function CaseProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<CaseState>(initial);
  const setCase = useCallback((caseId: string, jobId: string | null = null) => { const next = { caseId, jobId }; setState(next); try { sessionStorage.setItem(key, JSON.stringify(next)); } catch { /* storage may be disabled */ } }, []);
  const reset = useCallback(() => { setState({ caseId: null, jobId: null }); try { sessionStorage.removeItem(key); } catch { /* storage may be disabled */ } }, []);
  const value = useMemo(() => ({ ...state, setCase, reset }), [state, setCase, reset]);
  return <CaseContext.Provider value={value}>{children}</CaseContext.Provider>;
}
export function useCase() { const value = useContext(CaseContext); if (!value) throw new Error('useCase requires CaseProvider'); return value; }
