
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

const getToken = () => localStorage.getItem("summarizer-token");

async function request(path, options = {}) {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Request failed.");
  return data;
}

export async function authenticate(path, email, password) {
  return request(`/auth/${path}`, {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function getCurrentUser() {
  return request("/auth/me");
}

export async function getHistory() {
  return request("/history");
}

export async function saveSummary(summary, inputText, summaryLength) {
  return request("/history", {
    method: "POST",
    body: JSON.stringify({
      input_text: inputText,
      summary: summary.summary,
      model: summary.model,
      summary_length: summaryLength,
      original_words: summary.original_words,
      summary_words: summary.summary_words,
      processing_time_seconds: summary.processing_time_seconds,
    }),
  });
}

export async function summarizeText({
  text,
  model,
  summaryLength,
}) {
  return request("/summarize", {
    method: "POST",
    body: JSON.stringify({
      text,
      model,
      summary_length: summaryLength,
    }),
  });
}
