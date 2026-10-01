import type { ReactNode } from 'react';
import { isDemo } from '../../api/client';
import { disclaimer } from '../../lib/format';
import { Button } from '../ui/button';
import { Skeleton } from '../ui/skeleton';
export function DisclaimerBanner() { return <div className="border-b border-warning/30 bg-warning/10 px-4 py-2 text-center text-xs leading-5 text-foreground print:hidden" role="note"><strong className="mr-2 font-mono text-warning">RESEARCH PROTOTYPE</strong>{disclaimer}</div>; }
export function ResearchBadge() { return <span className="inline-flex rounded-input border border-warning/50 px-2 py-1 font-mono text-[10px] font-semibold tracking-widest text-warning">RESEARCH PROTOTYPE</span>; }
export function DemoBadge() { return isDemo ? <span className="rounded-input border border-warning px-2 py-1 font-mono text-xs text-warning">DEMO DATA</span> : null; }
export function EmptyState({ title, detail }: { title: string; detail?: string }) { return <div className="rounded-card border border-border bg-surface p-6"><h2 className="font-heading text-lg">{title}</h2>{detail && <p className="mt-2 text-sm text-muted">{detail}</p>}</div>; }
export function DataState({ loading, error, retry, children }: { loading: boolean; error: Error | null; retry: () => void; children: ReactNode }) { if (loading) return <div aria-label="Loading data" role="status" className="space-y-4"><Skeleton className="h-16 w-full"/><Skeleton className="h-40 w-full"/></div>; if (error) return <div role="alert" className="rounded-card border border-danger/50 p-6"><p className="mb-4 text-danger">{error.message}</p><Button variant="outline" onClick={retry}>Retry request</Button></div>; return <>{children}</>; }
