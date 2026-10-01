export type PredictedClass = 'HGG' | 'LGG';
export type Modality = 'T1' | 'T1ce' | 'T2' | 'FLAIR';
export interface HealthResponse { status: string; project: string; service: string }
export interface Patient { patient_id: string }
export interface PatientsResponse { count: number; patients: string[] }
export interface ModelPrediction { class: PredictedClass; hgg_probability: number; model_confidence: number }
export interface GroundTruth { class: PredictedClass; available: boolean }
export interface TumorROI { tumor_pixels: number; roi_pixels: number; tumor_fraction: number }
export interface Explainability { method: string; target_layer: string; mean_activation?: number; maximum_activation?: number; visualization?: string }
export interface PatientReport {
  patient_id: string; project: string; project_description: string; analysis_type: string;
  generated_at: string; mri_modalities: string[]; model_prediction: ModelPrediction;
  ground_truth?: GroundTruth; tumor_roi?: TumorROI; explainability?: Explainability; system_note?: string;
}
export interface ExplanationResponse { patient_id: string; available: boolean; filename: string }
export interface ModelMetrics { accuracy: number; precision: number; recall: number; f1: number }
export interface Metrics {
  classical_cnn: ModelMetrics; cerebraq: ModelMetrics; cerebraq_no_qft: ModelMetrics;
  cerebraq_no_entanglement: ModelMetrics; cerebraq_direct_angle_injection: ModelMetrics;
}
export interface ApiError { message: string; status?: number; code: 'http' | 'network' | 'invalid_response' | 'unavailable' }
export interface PipelineStage { id: string; title: string; description: string; inputShape?: string; outputShape?: string; durationMs?: number }
export interface PipelineData { stages: PipelineStage[]; nQubits?: number; circuitDepth?: number; backend?: string }
export interface ReportData { patient: PatientReport; explanation?: ExplanationResponse }
export interface AnalyzeRequest { files: Partial<Record<Modality, File>> }
export interface AnalyzeResponse { caseId: string; jobId?: string }
