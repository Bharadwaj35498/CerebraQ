import { NavLink, Outlet } from 'react-router-dom';
import * as Dialog from '@radix-ui/react-dialog';
import { Activity, BookOpen, Brain, ChartNoAxesCombined, FileText, Home, Menu, ScanSearch, X } from 'lucide-react';
import { useState } from 'react';
import { DisclaimerBanner, DemoBadge } from '../components/common/ResearchStates';
import { ThemeToggle } from './ThemeToggle';
import { useCase } from '../context/CaseContext';
const navigation = [
  { to: '/', label: 'Home', icon: Home, end: true }, { to: '/analyze', label: 'Analyze', icon: ScanSearch },
  { to: '/results', label: 'Results', icon: Brain }, { to: '/explainability', label: 'Explainability', icon: Activity },
  { to: '/reports', label: 'Reports', icon: FileText }, { to: '/performance', label: 'Model Performance', icon: ChartNoAxesCombined },
  { to: '/about', label: 'About', icon: BookOpen },
];
function Links({ close }: { close?: () => void }) { return <nav aria-label="Main navigation" className="flex flex-col gap-1">{navigation.map(({ to, label, icon: Icon, end }) => <NavLink key={to} to={to} end={end} onClick={close} className={({ isActive }) => `flex min-h-11 items-center gap-3 rounded-input border-l-2 px-3 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-classical ${isActive ? 'border-classical bg-classical/10 font-semibold text-foreground' : 'border-transparent text-muted hover:bg-elevated hover:text-foreground'}`}><Icon aria-hidden="true" size={18}/>{label}</NavLink>)}</nav>; }
export function AppShell() {
  const [open, setOpen] = useState(false);
  const { caseId } = useCase();
  return <div className="min-h-screen bg-background text-foreground"><a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:bg-surface focus:p-3">Skip to content</a><DisclaimerBanner/>
    <div className="flex min-h-[calc(100vh-44px)]"><aside className="hidden w-60 shrink-0 border-r border-border bg-surface px-4 py-6 md:block print:hidden"><div className="mb-9 border-b border-border pb-6"><div className="font-heading text-xl font-semibold">Cerebra<span className="text-classical">Q</span></div><div className="mt-1 font-mono text-[10px] tracking-widest text-muted">RESEARCH WORKSTATION</div></div><Links/></aside>
      <div className="min-w-0 flex-1"><header className="flex min-h-16 items-center justify-between gap-3 border-b border-border bg-surface px-4 md:px-8 print:hidden"><div className="flex min-w-0 items-center gap-3"><Dialog.Root open={open} onOpenChange={setOpen}><Dialog.Trigger asChild><button type="button" aria-label="Open navigation" className="rounded-input border border-border p-2 md:hidden"><Menu size={19}/></button></Dialog.Trigger><Dialog.Portal><Dialog.Overlay className="fixed inset-0 z-40 bg-background/80"/><Dialog.Content className="fixed inset-y-0 left-0 z-50 w-[min(19rem,85vw)] border-r border-border bg-surface p-5 shadow-lg"><Dialog.Title className="mb-6 font-heading text-xl">CerebraQ navigation</Dialog.Title><Dialog.Close className="absolute right-4 top-4 rounded-input p-2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-classical" aria-label="Close navigation"><X size={18}/></Dialog.Close><Links close={() => setOpen(false)}/></Dialog.Content></Dialog.Portal></Dialog.Root><span className="font-heading text-sm font-semibold md:hidden">CerebraQ</span><span className="hidden truncate font-mono text-xs text-muted sm:block">ACTIVE CASE: {caseId ?? 'NONE SELECTED'}</span></div><div className="flex items-center gap-3"><DemoBadge/><ThemeToggle/></div></header><main id="main" className="mx-auto w-full max-w-[1480px] p-4 pb-16 md:p-8"><Outlet/></main></div></div>
  </div>;
}
