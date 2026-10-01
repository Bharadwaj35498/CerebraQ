import { cn } from '../../lib/cn';
export function Skeleton({ className }: { className?: string }) { return <div aria-hidden="true" className={cn('animate-pulse rounded-input bg-elevated motion-reduce:animate-none', className)} />; }
