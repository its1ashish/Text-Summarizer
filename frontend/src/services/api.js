
const API_BASE_URL = "http://127.0.0.1:8000/api";

export async function summarizeText({
  text,
  model,
  summaryLength,
}) {
  const response = await fetch(`${API_BASE_URL}/summarize`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      text,
      model,
      summary_length: summaryLength,
    }),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message =
      typeof data.detail === "string"
        ? data.detail
        : "Unable to generate the summary.";

    throw new Error(message);
  }

  return data;
}
