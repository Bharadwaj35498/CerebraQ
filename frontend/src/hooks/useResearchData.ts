import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
export const usePatients = () => useQuery({ queryKey: ['patients'], queryFn: api.getPatients });
export const useMetrics = () => useQuery({ queryKey: ['metrics'], queryFn: api.getMetrics, staleTime: 300_000 });
export const useAnalysisResult = (id: string | null) => useQuery({ queryKey: ['patient', id], queryFn: () => api.getPatient(id ?? ''), enabled: Boolean(id) });
export const useExplainability = (id: string | null) => useQuery({ queryKey: ['explanation', id], queryFn: () => api.getExplanation(id ?? ''), enabled: Boolean(id) });
