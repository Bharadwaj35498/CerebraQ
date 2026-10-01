import { lazy, Suspense, type ReactNode } from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { AppShell } from '../layout/AppShell';
import { Skeleton } from '../components/ui/skeleton';
const Home = lazy(() => import('../pages/Home'));
const Analyze = lazy(() => import('../pages/Analyze'));
const Results = lazy(() => import('../pages/Results'));
const Explainability = lazy(() => import('../pages/Explainability'));
const Reports = lazy(() => import('../pages/Reports'));
const Performance = lazy(() => import('../pages/Performance'));
const About = lazy(() => import('../pages/About'));
function Loading() { return <div role="status" aria-label="Loading page" className="space-y-4"><Skeleton className="h-8 w-44"/><Skeleton className="h-48 w-full"/></div>; }
function ErrorPage() { return <main className="min-h-screen bg-background p-8 text-foreground"><h1 className="font-heading text-xl">Page unavailable</h1><p className="mt-3 text-muted">The requested route could not be displayed.</p><a className="mt-4 inline-block text-classical underline" href="/">Return home</a></main>; }
const page = (element: ReactNode) => <Suspense fallback={<Loading/>}>{element}</Suspense>;
const router = createBrowserRouter([{ path: '/', element: <AppShell/>, errorElement: <ErrorPage/>, children: [
  { index: true, element: page(<Home/>) }, { path: 'analyze', element: page(<Analyze/>) }, { path: 'results', element: page(<Results/>) },
  { path: 'explainability', element: page(<Explainability/>) }, { path: 'reports', element: page(<Reports/>) },
  { path: 'performance', element: page(<Performance/>) }, { path: 'about', element: page(<About/>) }, { path: '*', element: <ErrorPage/> },
] }]);
export function AppRouter() { return <RouterProvider router={router}/>; }
