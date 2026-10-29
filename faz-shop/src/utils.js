// src/utils.js
const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

export function resolveImageUrl(url) {
  if (!url) return '';
  if (/^(https?:|data:|blob:)/i.test(url)) return url;
  return `${API_BASE}${url.startsWith('/') ? '' : '/'}${url}`;
}