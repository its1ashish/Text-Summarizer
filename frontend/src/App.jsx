
import { useState } from "react";
import "./App.css";
import { summarizeText } from "./services/api";

const models = [
  {
    id: "textrank",
    name: "TextRank",
    type: "Extractive",
    description: "Selects important sentences from your text.",
  },
  {
    id: "t5",
    name: "T5-small",
    type: "Abstractive",
    description: "Generates a concise, rephrased summary.",
  },
  {
    id: "bart",
    name: "BART",
    type: "Abstractive",
    description: "Produces fluent summaries using a transformer model.",
  },
];

function App() {
  const [text, setText] = useState("");
  const [selectedModel, setSelectedModel] = useState("bart");
  const [summaryLength, setSummaryLength] = useState("medium");
  const [status, setStatus] = useState("");
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copyStatus, setCopyStatus] = useState("");
  const [comparisonResults, setComparisonResults] = useState([]);
  const [comparing, setComparing] = useState(false);

  const wordCount = text.trim()
    ? text.trim().split(/\s+/).length
    : 0;

  const characterCount = text.length;

  function handleTextChange(event) {
    setText(event.target.value);
    setStatus("");
    setSummary(null);
    setCopyStatus("");
    setComparisonResults([]);
  }

  function handleClear() {
    setText("");
    setStatus("");
    setSummary(null);
    setCopyStatus("");
    setComparisonResults([]);
  }



  async function handleSummarize() {
    if (!text.trim()) {
      setStatus("Please enter some text to summarize.");
      return;
    }

    if (text.trim().length > 50000) {
      setStatus("Your text must be 50,000 characters or fewer.");
      return;
    }

    setLoading(true);
    setStatus("");
    setCopyStatus("");
    setSummary(null);

    try {
      const data = await summarizeText({
        text: text.trim(),
        model: selectedModel,
        summaryLength,
      });

      setSummary(data);
    } catch (error) {
      setStatus(
        error.message ||
        "Unable to connect to the summarization server."
      );
    } finally {
      setLoading(false);
    }
  }


  async function handleCompare() {
    const input = text.trim();

    if (!input) {
      setStatus("Please enter some text to summarize.");
      return;
    }

    if (input.length > 50000) {
      setStatus("Your text must be 50,000 characters or fewer.");
      return;
    }

    setComparing(true);
    setStatus("");
    setSummary(null);
    setCopyStatus("");
    setComparisonResults([]);

    const results = [];

    try {
      for (let i = 0; i < models.length; i++) {
        const model = models[i];

        setStatus(
          `Comparing models (${i + 1}/${models.length}): ${model.name}...`
        );

        try {
          const data = await summarizeText({
            text: input,
            model: model.id,
            summaryLength,
          });

          results.push({
            ...data,
            modelName: model.name,
            modelType: model.type,
            error: null,
          });
        } catch (error) {
          results.push({
            modelName: model.name,
            modelType: model.type,
            error: error.message || "Summarization failed.",
          });
        }

        // Show each result as soon as it finishes.
        setComparisonResults([...results]);
      }

      const failures = results.filter((result) => result.error).length;

      setStatus(
        failures === 0
          ? "Comparison complete."
          : `Comparison finished with ${failures} model failure(s).`
      );
    } finally {
      setComparing(false);
    }
  }



  async function handleCopy() {
    if (!summary?.summary) return;

    try {
      await navigator.clipboard.writeText(summary.summary);
      setCopyStatus("Summary copied to clipboard.");
    } catch {
      setCopyStatus(
        "Unable to copy automatically. Please select and copy the summary."
      );
    }
  }



  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#home">
          <span className="brand-icon">S</span>
          <span>SummarAI</span>
        </a>

        <div className="sidebar-label">WORKSPACE</div>

        <nav className="navigation">
          <a className="nav-item active" href="#summarizer">
            <span className="nav-symbol">▤</span>
            Summarizer
          </a>

          <a className="nav-item" href="#history">
            <span className="nav-symbol">◷</span>
            History
            <span className="coming-soon">Soon</span>
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="local-indicator">
            <span className="status-dot" />
            <div>
              <strong>Local project</strong>
              <p>Python NLP models</p>
            </div>
          </div>
          <p className="sidebar-footer">
            Text Summarizer · v1.0
          </p>
        </div>
      </aside>

      <main className="main-content" id="summarizer">
        <header className="topbar">
          <span className="breadcrumb">
            Workspace <span>/</span> Summarizer
          </span>
          <span className="prototype-badge">
            Frontend prototype
          </span>
        </header>

        <section className="page-content">
          <div className="page-heading">
            <span className="eyebrow">AI-POWERED WRITING TOOL</span>
            <h1>Make your text work smarter.</h1>
            <p>
              Turn lengthy articles and documents into concise,
              meaningful summaries.
            </p>
          </div>

          <section className="editor-card">
            <div className="section-heading">
              <div>
                <h2>Original text</h2>
                <p>Paste the content you want to summarize.</p>
              </div>
              <button
                className="text-button"
                onClick={handleClear}
                disabled={!text}
                type="button"
              >
                Clear text
              </button>
            </div>

            <textarea
              className="text-editor"
              value={text}
              onChange={handleTextChange}
              disabled={comparing}
              placeholder="Paste an article, research paper, blog post, or any lengthy text here..."
              aria-label="Original text"
            />

            <div className="editor-footer">
              <span>{wordCount.toLocaleString()} words</span>
              <span>{characterCount.toLocaleString()} characters</span>
            </div>
          </section>

          <section className="settings-section">
            <div className="section-heading">
              <div>
                <h2>Choose your model</h2>
                <p>Compare extractive and abstractive summarization.</p>
              </div>
            </div>

            <div className="model-grid">
              {models.map((model) => (
                <button
                  key={model.id}
                  type="button"
                  className={`model-card ${selectedModel === model.id ? "selected" : ""
                    }`}
                  onClick={() => {
                    setSelectedModel(model.id);
                    setStatus("");
                  }}
                  aria-pressed={selectedModel === model.id}
                >
                  <div className="model-card-top">
                    <span className="model-name">{model.name}</span>
                    <span className="radio-indicator">
                      {selectedModel === model.id ? "✓" : ""}
                    </span>
                  </div>

                  <span className="model-type">{model.type}</span>
                  <p>{model.description}</p>
                </button>
              ))}
            </div>
          </section>

          <section className="settings-section length-section">
            <div className="section-heading">
              <div>
                <h2>Summary length</h2>
                <p>Choose how concise you want your result to be.</p>
              </div>
            </div>

            <div className="length-options">
              {[
                { id: "short", label: "Short", detail: "Key points" },
                { id: "medium", label: "Medium", detail: "Balanced" },
                { id: "long", label: "Long", detail: "More detail" },
              ].map((option) => (
                <button
                  key={option.id}
                  type="button"
                  className={`length-option ${summaryLength === option.id ? "selected" : ""
                    }`}
                  onClick={() => {
                    setSummaryLength(option.id);
                    setStatus("");
                  }}
                  aria-pressed={summaryLength === option.id}
                >
                  <span>{option.label}</span>
                  <small>{option.detail}</small>
                </button>
              ))}
            </div>
          </section>

          <div className="action-area">

            <button
              className="summarize-button"
              type="button"
              onClick={handleSummarize}
              disabled={loading}
            >
              <span aria-hidden="true">
                {loading ? "◌" : "✦"}
              </span>
              {loading ? "Generating summary..." : "Summarize text"}
            </button>

            {status && (
              <p className="status-message" role="status">
                {status}
              </p>
            )}

            <button
              className="compare-button"
              type="button"
              onClick={handleCompare}
              disabled={loading || comparing}
            >
              {comparing ? "Comparing models..." : "Compare all 3 models"}
            </button>


          </div>


          <section className="result-card">
            <div className="section-heading">
              <div>
                <h2>Your summary</h2>
                <p>
                  {summary
                    ? `Generated using ${models.find((m) => m.id === summary.model)?.name ||
                    summary.model
                    }`
                    : "Your generated summary will appear here."}
                </p>
              </div>

              <button
                className="copy-button"
                type="button"
                onClick={handleCopy}
                disabled={!summary?.summary}
              >
                Copy summary
              </button>
            </div>

            {summary ? (
              <div className="summary-content">
                <p className="summary-text">{summary.summary}</p>

                <div className="summary-stats">
                  <div>
                    <strong>{summary.original_words}</strong>
                    <span>Original words</span>
                  </div>

                  <div>
                    <strong>{summary.summary_words}</strong>
                    <span>Summary words</span>
                  </div>

                  <div>
                    <strong>
                      {summary.original_words > 0
                        ? `${Math.round(
                          (1 -
                            summary.summary_words /
                            summary.original_words) *
                          100
                        )}%`
                        : "—"}
                    </strong>
                    <span>Word reduction</span>
                  </div>

                  <div>
                    <strong>{summary.processing_time_seconds}s</strong>
                    <span>Processing time</span>
                  </div>
                </div>

                {copyStatus && (
                  <p className="status-message" role="status">
                    {copyStatus}
                  </p>
                )}
              </div>
            ) : (
              <div className="empty-result">
                <div className="empty-result-icon">✧</div>
                <h3>{loading ? "Generating your summary" : "Ready when you are"}</h3>
                <p>
                  {loading
                    ? "Your selected model is processing the text. This may take a little while."
                    : "Enter your text, select a model, and click Summarize text to see the result here."}
                </p>
              </div>
            )}
          </section>


          {comparisonResults.length > 0 && (
            <section className="comparison-section">
              <div className="section-heading">
                <div>
                  <h2>Model comparison</h2>
                  <p>
                    Results for the same input and summary length.
                  </p>
                </div>
              </div>

              <div className="comparison-grid">
                {comparisonResults.map((result) => (
                  <article
                    className="comparison-card"
                    key={result.modelName}
                  >
                    <div className="comparison-card-heading">
                      <div>
                        <h3>{result.modelName}</h3>
                        <span className="comparison-model-type">
                          {result.modelType}
                        </span>
                      </div>
                    </div>

                    {result.error ? (
                      <p className="comparison-error" role="alert">
                        {result.error}
                      </p>
                    ) : (
                      <>
                        <p className="comparison-summary">
                          {result.summary}
                        </p>

                        <div className="comparison-metrics">
                          <div>
                            <strong>{result.summary_words}</strong>
                            <span>Words</span>
                          </div>

                          <div>
                            <strong>
                              {result.original_words > 0
                                ? `${Math.round(
                                  (1 -
                                    result.summary_words /
                                    result.original_words) *
                                  100
                                )}%`
                                : "—"}
                            </strong>
                            <span>Word reduction</span>
                          </div>

                          <div>
                            <strong>
                              {result.processing_time_seconds}s
                            </strong>
                            <span>Time</span>
                          </div>
                        </div>

                        <button
                          className="text-button"
                          type="button"
                          onClick={async () => {
                            try {
                              await navigator.clipboard.writeText(
                                result.summary
                              );
                              setCopyStatus(
                                `${result.modelName} summary copied.`
                              );
                            } catch {
                              setCopyStatus(
                                "Unable to copy automatically."
                              );
                            }
                          }}
                        >
                          Copy this summary
                        </button>
                      </>
                    )}
                  </article>
                ))}
              </div>

              {comparing && (
                <p className="comparison-progress" role="status">
                  Generating summaries sequentially. This can take a
                  while, especially when a model loads for the first time.
                </p>
              )}

              {copyStatus && (
                <p className="status-message" role="status">
                  {copyStatus}
                </p>
              )}
            </section>
          )}


          <footer className="page-footer">
            Text Summarizer · Powered by your NLP models
          </footer>
        </section>
      </main>
    </div>
  );
}

export default App;

