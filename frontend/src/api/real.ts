import type { AnalyzeRequest, AnalyzeResponse, ExplanationResponse, HealthResponse, Metrics, PatientReport, PatientsResponse } from '../types/api';

export class ApiRequestError extends Error {
  constructor(message: string, public readonly code: 'http' | 'network' | 'invalid_response' | 'unavailable', public readonly status?: number) { super(message); this.name = 'ApiRequestError'; }
}

const base = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/+$/, '');
async function request(path: string): Promise<unknown> {
  let response: Response;
  try { response = await fetch(`${base}${path}`, { headers: { Accept: 'application/json' } }); }
  catch { throw new ApiRequestError('Backend unavailable. Check the Flask server and browser connectivity.', 'network'); }
  if (!response.ok) throw new ApiRequestError(response.status === 404 ? 'Requested resource is not available.' : `Request failed (${response.status}).`, 'http', response.status);
  try { return await response.json() as unknown; } catch { throw new ApiRequestError('Invalid JSON returned by backend.', 'invalid_response'); }
}
const record = (v: unknown): v is Record<string, unknown> => typeof v === 'object' && v !== null && !Array.isArray(v);
const number = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v);
const fraction = (v: unknown): v is number => number(v) && v >= 0 && v <= 1;
const text = (v: unknown): v is string => typeof v === 'string';
const grade = (v: unknown): v is 'HGG' | 'LGG' => v === 'HGG' || v === 'LGG';
function invalid(): never { throw new ApiRequestError('Backend response has an unexpected structure.', 'invalid_response'); }
function parseHealth(v: unknown): HealthResponse { if (!record(v) || !text(v.status) || !text(v.project) || !text(v.service)) return invalid(); return { status: v.status, project: v.project, service: v.service }; }
function parsePatients(v: unknown): PatientsResponse { if (!record(v) || !number(v.count) || !Array.isArray(v.patients) || !v.patients.every(text)) return invalid(); return { count: v.count, patients: v.patients }; }
function parsePatient(v: unknown): PatientReport {
  if (!record(v) || !text(v.patient_id) || !text(v.project) || !text(v.project_description) || !text(v.analysis_type) || !text(v.generated_at) || !Array.isArray(v.mri_modalities) || !v.mri_modalities.every(text) || !record(v.model_prediction)) return invalid();
  const p = v.model_prediction;
  if (!grade(p.class) || !fraction(p.hgg_probability) || !fraction(p.model_confidence)) return invalid();
  let ground_truth: PatientReport['ground_truth'];
  if (record(v.ground_truth)) { if (!grade(v.ground_truth.class) || typeof v.ground_truth.available !== 'boolean') return invalid(); ground_truth = { class: v.ground_truth.class, available: v.ground_truth.available }; }
  let tumor_roi: PatientReport['tumor_roi'];
  if (record(v.tumor_roi)) { const r = v.tumor_roi; if (!number(r.tumor_pixels) || !number(r.roi_pixels) || !fraction(r.tumor_fraction)) return invalid(); tumor_roi = { tumor_pixels: r.tumor_pixels, roi_pixels: r.roi_pixels, tumor_fraction: r.tumor_fraction }; }
  let explainability: PatientReport['explainability'];
  if (record(v.explainability)) { const e = v.explainability; if (!text(e.method) || !text(e.target_layer)) return invalid(); explainability = { method: e.method, target_layer: e.target_layer, mean_activation: number(e.mean_activation) ? e.mean_activation : undefined, maximum_activation: number(e.maximum_activation) ? e.maximum_activation : undefined, visualization: text(e.visualization) ? e.visualization : undefined }; }
  return { patient_id: v.patient_id, project: v.project, project_description: v.project_description, analysis_type: v.analysis_type, generated_at: v.generated_at, mri_modalities: v.mri_modalities, model_prediction: { class: p.class, hgg_probability: p.hgg_probability, model_confidence: p.model_confidence }, ground_truth, tumor_roi, explainability, system_note: text(v.system_note) ? v.system_note : undefined };
}
function parseExplanation(v: unknown): ExplanationResponse { if (!record(v) || !text(v.patient_id) || typeof v.available !== 'boolean' || !text(v.filename)) return invalid(); return { patient_id: v.patient_id, available: v.available, filename: v.filename }; }
const keys = ['classical_cnn', 'cerebraq', 'cerebraq_no_qft', 'cerebraq_no_entanglement', 'cerebraq_direct_angle_injection'] as const;
function parseMetrics(v: unknown): Metrics {
  if (!record(v)) return invalid();
  const result: Partial<Metrics> = {};
  for (const key of keys) { const row = v[key]; if (!record(row) || !fraction(row.accuracy) || !fraction(row.precision) || !fraction(row.recall) || !fraction(row.f1)) return invalid(); result[key] = { accuracy: row.accuracy, precision: row.precision, recall: row.recall, f1: row.f1 }; }
  return result as Metrics;
}
export const realApi = {
  health: async () => parseHealth(await request('/api/health')),
  getPatients: async () => parsePatients(await request('/api/patients')),
  getPatient: async (id: string) => parsePatient(await request(`/api/patient/${encodeURIComponent(id)}`)),
  getMetrics: async () => parseMetrics(await request('/api/metrics')),
  getExplanation: async (id: string) => parseExplanation(await request(`/api/explanation/${encodeURIComponent(id)}`)),
  analyze: async (_input: AnalyzeRequest): Promise<AnalyzeResponse> => { throw new ApiRequestError('Analysis upload is not available: the current Flask backend has no analysis endpoint.', 'unavailable'); },
};
