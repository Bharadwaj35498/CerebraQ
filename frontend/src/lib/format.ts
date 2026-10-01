export const percent = (value?: number | null) => value === undefined || value === null ? 'Not available' : `${(value * 100).toFixed(2)}%`;
export const dateTime = (value?: string) => { if (!value) return 'Not available'; const date = new Date(value); return Number.isNaN(date.getTime()) ? value : date.toLocaleString(); };
export const disclaimer = 'This output is a research-model prediction and is not a clinical diagnosis or a replacement for professional medical interpretation.';
