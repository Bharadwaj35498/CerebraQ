import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import { CaseProvider } from '../context/CaseContext';
const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 60_000, retry: 1, refetchOnWindowFocus: false } } });
export function Providers({ children }: { children: ReactNode }) { return <QueryClientProvider client={queryClient}><CaseProvider>{children}</CaseProvider></QueryClientProvider>; }
