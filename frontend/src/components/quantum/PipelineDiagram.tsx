import { useState } from 'react';
import type { PipelineStage } from '../../types/api';
const stages: PipelineStage[] = [
  { id: 'preprocess', title: 'Preprocessing', description: 'Modality alignment and normalization prepare MRI data for research analysis.' },
  { id: 'roi', title: 'Tumour ROI', description: 'The tumour region of interest focuses the subsequent feature extraction.' },
  { id: 'cnn', title: 'Classical CNN', description: 'Convolutional feature extraction forms the classical branch.' },
  { id: 'quantum', title: 'Quantum Processing', description: 'Encoded features pass through a simulator-based parameterized circuit.' },
  { id: 'hybrid', title: 'Hybrid Classifier', description: 'Classical and quantum features inform the HGG/LGG research-model output.' },
];
export function PipelineDiagram() {
  const [selected, setSelected] = useState<PipelineStage | null>(null);
  return <section aria-label="Research processing pipeline"><div className="grid gap-2 sm:grid-cols-5">{stages.map((stage, index) => <button key={stage.id} type="button" aria-pressed={selected?.id === stage.id} onClick={() => setSelected(selected?.id === stage.id ? null : stage)} className={`min-h-24 rounded-card border p-3 text-left transition-colors hover:bg-elevated ${stage.id === 'quantum' ? 'border-quantum' : stage.id === 'hybrid' ? 'border-l-classical border-r-quantum border-y-border' : 'border-classical/50'}`}><span className="font-mono text-[10px] text-muted">STAGE {String(index + 1).padStart(2, '0')}</span><strong className="mt-2 block text-sm">{stage.title}</strong></button>)}</div>{selected && <StageDetailPanel stage={selected}/>}</section>;
}
export function StageDetailPanel({ stage }: { stage: PipelineStage }) { return <div className="mt-4 rounded-card border border-border bg-surface p-5"><h3 className="font-heading text-base">{stage.title}</h3><p className="mt-2 text-sm text-muted">{stage.description}</p><dl className="mt-4 grid gap-3 font-mono text-xs sm:grid-cols-3"><div>Input shape: {stage.inputShape ?? 'Not available'}</div><div>Output shape: {stage.outputShape ?? 'Not available'}</div><div>Duration: {stage.durationMs === undefined ? 'Not available' : `${stage.durationMs} ms`}</div></dl></div>; }
