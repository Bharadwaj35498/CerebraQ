import { ApiRequestError } from './real';
import type { AnalyzeRequest, AnalyzeResponse, ExplanationResponse, HealthResponse, Metrics, PatientReport, PatientsResponse } from '../types/api';
// No fabricated patient records or research metrics are shipped in demo mode.
const unavailable = (): never => { throw new ApiRequestError('Demo dataset is not configured. Switch to the real Flask backend.', 'unavailable'); };
export const mockApi = {
  health: async (): Promise<HealthResponse> => unavailable(),
  getPatients: async (): Promise<PatientsResponse> => unavailable(),
  getPatient: async (id: string): Promise<PatientReport> => { void id; return unavailable(); },
  getMetrics: async (): Promise<Metrics> => unavailable(),
  getExplanation: async (id: string): Promise<ExplanationResponse> => { void id; return unavailable(); },
  analyze: async (input: AnalyzeRequest): Promise<AnalyzeResponse> => { void input; return unavailable(); },
};
