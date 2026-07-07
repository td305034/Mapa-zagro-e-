const API_URL = import.meta.env.VITE_API_URL;

export default async function checkHealth() {
  const res = await fetch(`${API_URL}/health`);
  return res.json();
}

export async function getRisks() {
  const res = await fetch(`${API_URL}/risks/`);
  if (!res.ok) {
    throw new Error(`GET /risks/ failed: ${res.status}`);
  }
  return res.json();
}

function formatApiError(body) {
  const detail = body?.detail;
  if (!detail) return null;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => (typeof item === "string" ? item : item.msg))
      .filter(Boolean)
      .join(" ");
  }
  return null;
}

export async function createRisk(payload) {
  const res = await fetch(`${API_URL}/risks/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(
      formatApiError(body) || `POST /risks/ failed: ${res.status}`
    );
  }
  return res.json();
}
