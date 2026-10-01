import { forwardRef, type ButtonHTMLAttributes } from 'react';
import { cn } from '../../lib/cn';
type Props = ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'default' | 'outline' | 'ghost' };
export const Button = forwardRef<HTMLButtonElement, Props>(function Button({ className, variant = 'default', type = 'button', ...props }, ref) {
  return <button ref={ref} type={type} className={cn('inline-flex min-h-10 items-center justify-center gap-2 rounded-input px-4 py-2 text-sm font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-classical disabled:cursor-not-allowed disabled:opacity-50', variant === 'default' ? 'bg-classical text-background hover:bg-classical/80' : variant === 'outline' ? 'border border-border bg-surface text-foreground hover:bg-elevated' : 'text-foreground hover:bg-elevated', className)} {...props} />;
});
