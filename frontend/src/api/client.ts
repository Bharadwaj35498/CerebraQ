import { mockApi } from './mock';
import { realApi } from './real';
export const isDemo = import.meta.env.VITE_USE_MOCK === 'true';
export const api = isDemo ? mockApi : realApi;
