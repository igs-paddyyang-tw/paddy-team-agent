const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:33333";

export function getApiKey(): string {
  if (typeof window === "undefined") return "";
  return localStorage.getItem("ark_api_key") || "";
}

export function setApiKey(key: string) {
  localStorage.setItem("ark_api_key", key);
}

export function clearApiKey() {
  localStorage.removeItem("ark_api_key");
}

async function request(path: string, options: RequestInit = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "X-API-Key": getApiKey(), "Content-Type": "application/json", ...options.headers },
  });
  if (res.status === 401) {
    clearApiKey();
    if (typeof window !== "undefined") window.location.href = "/login";
    throw new Error("Unauthorized");
  }
  return res.json();
}

export const api = {
  get: (path: string) => request(path),
  post: (path: string, body: unknown) => request(path, { method: "POST", body: JSON.stringify(body) }),
  patch: (path: string, body: unknown) => request(path, { method: "PATCH", body: JSON.stringify(body) }),
  delete: (path: string) => request(path, { method: "DELETE" }),
};

export const fetcher = (path: string) => api.get(path);
