import { useRef, useState } from 'react';
import { Button } from '../ui/button';
import type { Modality } from '../../types/api';
interface ScanViewerProps {
  images: Partial<Record<Modality, string | null>>;
  overlay?: string | null;
  sliceImages?: string[];
  label?: string;
}
const modalities: Modality[] = ['T1', 'T1ce', 'T2', 'FLAIR'];
export function ScanViewer({ images, overlay, sliceImages, label = 'MRI research viewer' }: ScanViewerProps) {
  const [modality, setModality] = useState<Modality>('T1');
  const [opacity, setOpacity] = useState(50);
  const [slice, setSlice] = useState(0);
  const container = useRef<HTMLDivElement>(null);
  const image = sliceImages?.[slice] ?? images[modality];
  return <section ref={container} aria-label={label} className="rounded-card border border-border bg-surface p-4 fullscreen:overflow-auto fullscreen:bg-surface"><div className="mb-3 flex flex-wrap items-center justify-between gap-3"><h3 className="font-heading text-sm">Scan viewer</h3><div className="flex flex-wrap gap-2"><Button variant="outline" onClick={() => { setModality('T1'); setOpacity(50); setSlice(0); }}>Reset view</Button><Button variant="outline" onClick={() => { if (document.fullscreenElement) void document.exitFullscreen(); else void container.current?.requestFullscreen(); }}>Toggle fullscreen</Button></div></div><div className="relative flex aspect-square max-h-[65vh] min-h-56 items-center justify-center overflow-hidden border border-border bg-black sm:aspect-video">{image ? <img src={image} alt={`${modality} MRI ${sliceImages ? `slice ${slice + 1}` : 'image'}`} className="max-h-full max-w-full object-contain"/> : <p className="px-4 text-center font-mono text-xs text-muted">SCAN IMAGE NOT AVAILABLE</p>}{overlay && image && <img src={overlay} alt="Grad-CAM overlay" className="pointer-events-none absolute inset-0 h-full w-full object-contain transition-opacity motion-reduce:transition-none" style={{ opacity: opacity / 100 }}/>}</div><div className="mt-3 grid gap-4 text-xs sm:grid-cols-3"><label className="flex flex-col gap-2">Modality<select className="min-h-10 rounded-input border border-border bg-elevated p-2 font-mono" value={modality} onChange={event => setModality(event.target.value as Modality)}>{modalities.map(value => <option key={value} value={value}>{value}</option>)}</select></label><label className="flex flex-col gap-2">Overlay opacity: {overlay ? `${opacity}%` : 'Not available'}<input type="range" min="0" max="100" value={opacity} disabled={!overlay} onChange={event => setOpacity(Number(event.target.value))} aria-label="Overlay opacity"/></label><label className="flex flex-col gap-2">Slice: {sliceImages?.length ? `${slice + 1} / ${sliceImages.length}` : 'Not available'}<input type="range" min="0" max={Math.max(0, (sliceImages?.length ?? 1) - 1)} value={slice} disabled={!sliceImages?.length} onChange={event => setSlice(Number(event.target.value))} aria-label="MRI slice"/></label></div><p className="mt-3 font-mono text-[11px] text-muted">{modality} · {image ? 'IMAGE LOADED' : 'NO IMAGE'} · {overlay ? 'OVERLAY AVAILABLE' : 'NO OVERLAY'}</p></section>;
}
