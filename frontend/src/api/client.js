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
