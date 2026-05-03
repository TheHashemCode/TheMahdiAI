"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import styles from "../page.module.css";
import localStyles from "./notebooks.module.css";

interface Notebook {
  id: string;
  external_id: string;
  title: string;
  created_at: string;
}

interface Reference {
  document_id: string;
  text: string;
  title: string;
}

interface HistoryItem {
  id: string;
  notebook_title: string;
  question: string;
  answer: string;
  source: string;
  created_at: string;
}

export default function NotebooksPage() {
  const [notebooks, setNotebooks] = useState<Notebook[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  
  const [newTitle, setNewTitle] = useState("");
  const [activeNb, setActiveNb] = useState<string | null>(null);
  const [sources, setSources] = useState<any[]>([]);
  const [sourceUrl, setSourceUrl] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [references, setReferences] = useState<Reference[]>([]);
  const [querying, setQuerying] = useState(false);
  const [loadingSources, setLoadingSources] = useState(false);

  const [fallbackChain, setFallbackChain] = useState<string[]>([]);
  const [savingChain, setSavingChain] = useState(false);
  const [selectedHistory, setSelectedHistory] = useState<HistoryItem | null>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL ? `${process.env.NEXT_PUBLIC_API_URL}/admin/notebooks` : "http://localhost:8000/api/v1/admin/notebooks";
  const CONFIGS_API = process.env.NEXT_PUBLIC_API_URL ? `${process.env.NEXT_PUBLIC_API_URL}/admin/configs` : "http://localhost:8000/api/v1/admin/configs";

  const fetchData = async () => {
    try {
      const [nbRes, histRes, configRes] = await Promise.all([
        fetch(`${API_BASE}/`),
        fetch(`${API_BASE}/history`),
        fetch(CONFIGS_API)
      ]);
      const nbs = await nbRes.json();
      const hist = await histRes.json();
      const configs = await configRes.json();
      
      // Ensure we set arrays even if API returns error objects
      setNotebooks(Array.isArray(nbs) ? nbs : []);
      setHistory(Array.isArray(hist) ? hist : []);
      
      // Load fallback chain from config
      const chainConfig = Array.isArray(configs) ? configs.find(c => c.key === "notebook_fallback_chain") : null;
      if (chainConfig && chainConfig.value) {
        try {
          setFallbackChain(JSON.parse(chainConfig.value));
        } catch (e) {
          setFallbackChain([]);
        }
      }
      
      // Select first notebook by default if none selected
      if (!activeNb && Array.isArray(nbs) && nbs.length > 0) {
        setActiveNb(nbs[0].external_id);
      }
    } catch (err) {
      console.error("Failed to fetch data", err);
      setNotebooks([]);
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSaveChain = async () => {
    setSavingChain(true);
    try {
      await fetch(CONFIGS_API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key: "notebook_fallback_chain", value: JSON.stringify(fallbackChain) })
      });
      alert("Fallback chain saved successfully!");
    } catch (err) {
      alert("Failed to save chain.");
    } finally {
      setSavingChain(false);
    }
  };

  const fetchSources = async (nbId: string) => {
    setLoadingSources(true);
    try {
      const res = await fetch(`${API_BASE}/${nbId}/sources`);
      const data = await res.json();
      setSources(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to fetch sources", err);
      setSources([]);
    } finally {
      setLoadingSources(false);
    }
  };

  useEffect(() => {
    if (activeNb) {
      fetchSources(activeNb);
    } else {
      setSources([]);
    }
  }, [activeNb]);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await fetch(`${API_BASE}/sync`, { method: "POST" });
      await fetchData();
    } finally {
      setSyncing(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle) return;
    try {
      await fetch(`${API_BASE}/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: newTitle })
      });
      setNewTitle("");
      await fetchData();
    } catch (err) {
      alert("Failed to create notebook");
    }
  };

  const handleAddSource = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeNb || !sourceUrl) return;
    try {
      await fetch(`${API_BASE}/${activeNb}/sources`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: sourceUrl })
      });
      setSourceUrl("");
      alert("Source added successfully");
      fetchSources(activeNb);
    } catch (err) {
      alert("Failed to add source");
    }
  };

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeNb || !question) return;
    setQuerying(true);
    setAnswer("");
    setReferences([]);
    try {
      const res = await fetch(`${API_BASE}/${activeNb}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
      });
      const data = await res.json();
      setAnswer(data.answer);
      setReferences(data.references || []);
      await fetchData(); // Refresh history
    } catch (err) {
      alert("Failed to query notebook");
    } finally {
      setQuerying(false);
    }
  };

  const handleLogin = async () => {
    try {
      await fetch(`${API_BASE}/login`, { method: "POST" });
      alert("Browser opened on the server machine. Please log in there.");
    } catch (err) {
      alert("Failed to trigger login.");
    }
  };

  const formatAnswer = (text: string) => {
    if (!text) return "";
    // Bolds [1], [1, 2], [1-3]
    return text.replace(/\[([\d,\s-]+)\]/g, (match) => `**${match}**`);
  };

  return (
    <div className={styles.overviewStack}>
      <div className={styles.banner}>
        <div className={styles.bannerInfo}>
          <h2>NotebookLM Integration</h2>
          <p>Manage your Google NotebookLM connections and query history.</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button 
            className={localStyles.secondaryBtn} 
            onClick={handleLogin}
          >
            Login via UI (Server)
          </button>
          <button 
            className={localStyles.syncBtn} 
            onClick={handleSync}
            disabled={syncing}
          >
            {syncing ? "Syncing..." : "Sync from Google"}
          </button>
        </div>
      </div>

      <div className={localStyles.topControls}>
        <div className={localStyles.nbSelector}>
          <label>Select Notebook:</label>
          <select 
            value={activeNb || ""} 
            onChange={(e) => setActiveNb(e.target.value)}
            className={localStyles.select}
          >
            {notebooks.map(nb => (
              <option key={nb.id} value={nb.external_id}>
                {nb.title} ({nb.external_id})
              </option>
            ))}
          </select>
        </div>
        <form onSubmit={handleCreate} className={localStyles.createForm}>
          <input 
            type="text" 
            placeholder="New Notebook Title" 
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            className={localStyles.input}
          />
          <button type="submit" className={localStyles.primaryBtn}>Create</button>
        </form>
      </div>

      {activeNb && (
        <div className={localStyles.mainLayout}>
          <section className={`${styles.infoCard} ${localStyles.sourcesCard}`}>
            <div className={styles.cardTitle}>
              <h3>Sources ({sources.length})</h3>
            </div>
            
            <div className={localStyles.sourceList}>
              {loadingSources ? (
                <p className={localStyles.placeholder}>Loading sources...</p>
              ) : sources.length === 0 ? (
                <p className={localStyles.placeholder}>No sources found.</p>
              ) : (
                <ul>
                  {sources.map(src => (
                    <li key={src.id}>
                      <strong>{src.title}</strong>
                      <span>{src.id}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className={localStyles.addSourceForm}>
              <h4>Add New Source</h4>
              <form onSubmit={handleAddSource} className={localStyles.form}>
                <input 
                  type="url" 
                  placeholder="https://example.com/article" 
                  value={sourceUrl}
                  onChange={(e) => setSourceUrl(e.target.value)}
                  className={localStyles.input}
                />
                <button type="submit" className={localStyles.secondaryBtn}>Add URL</button>
              </form>
            </div>
          </section>

          <section className={`${styles.infoCard} ${localStyles.queryCard}`}>
            <div className={styles.cardTitle}>
              <h3>Test Query on: {notebooks.find(n => n.external_id === activeNb)?.title}</h3>
            </div>
            <form onSubmit={handleAsk} className={localStyles.queryForm}>
              <textarea 
                placeholder="Ask a question about the sources..." 
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className={localStyles.textarea}
              />
              <button type="submit" className={localStyles.primaryBtn} disabled={querying}>
                {querying ? "Thinking..." : "Ask AI"}
              </button>
            </form>
                {answer && (
              <div className={localStyles.answerBox}>
                <strong>Answer:</strong>
                <div className={localStyles.markdownBody}>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {formatAnswer(answer)}
                  </ReactMarkdown>
                </div>
              </div>
            )}

          </section>
        </div>
      )}


      <section className={styles.infoCard} style={{ marginBottom: '24px' }}>
        <div className={styles.cardTitle}>
          <h3>Telegram Bot: Fallback Chain Setup</h3>
        </div>
        <p className={localStyles.placeholder} style={{ padding: '10px 0', textAlign: 'left' }}>
          When users ask questions via the Telegram bot, it will query the first notebook in this chain. If it finds less than 2 references, it will automatically fallback to the next notebook, up to a maximum of 5 notebooks.
        </p>
        
        <div className={localStyles.chainBuilder}>
          <div className={localStyles.chainList}>
            {fallbackChain.map((nbId, index) => {
              const nbInfo = notebooks.find(n => n.external_id === nbId);
              return (
                <div key={`${nbId}-${index}`} className={localStyles.chainItem}>
                  <div className={localStyles.chainRank}>{index + 1}</div>
                  <div className={localStyles.chainTitle}>
                    {nbInfo ? nbInfo.title : nbId}
                  </div>
                  <div className={localStyles.chainControls}>
                    <button 
                      onClick={() => {
                        if (index > 0) {
                          const newChain = [...fallbackChain];
                          [newChain[index - 1], newChain[index]] = [newChain[index], newChain[index - 1]];
                          setFallbackChain(newChain);
                        }
                      }}
                      disabled={index === 0}
                    >↑</button>
                    <button 
                      onClick={() => {
                        if (index < fallbackChain.length - 1) {
                          const newChain = [...fallbackChain];
                          [newChain[index + 1], newChain[index]] = [newChain[index], newChain[index + 1]];
                          setFallbackChain(newChain);
                        }
                      }}
                      disabled={index === fallbackChain.length - 1}
                    >↓</button>
                    <button 
                      className={localStyles.removeBtn}
                      onClick={() => {
                        setFallbackChain(fallbackChain.filter((_, i) => i !== index));
                      }}
                    >✕</button>
                  </div>
                </div>
              );
            })}
            
            {fallbackChain.length === 0 && (
              <p className={localStyles.placeholder} style={{ padding: '20px 0' }}>No notebooks in fallback chain. Bot will not be able to answer.</p>
            )}
          </div>
          
          <div className={localStyles.chainAdder}>
            <select 
              className={localStyles.select} 
              id="add-chain-select"
              defaultValue=""
            >
              <option value="" disabled>-- Select Notebook to Add --</option>
              {notebooks.filter(n => !fallbackChain.includes(n.external_id)).map(nb => (
                <option key={nb.id} value={nb.external_id}>{nb.title}</option>
              ))}
            </select>
            <button 
              className={localStyles.secondaryBtn}
              onClick={() => {
                const selectEl = document.getElementById('add-chain-select') as HTMLSelectElement;
                if (selectEl && selectEl.value && fallbackChain.length < 5) {
                  setFallbackChain([...fallbackChain, selectEl.value]);
                  selectEl.value = ""; // Reset
                } else if (fallbackChain.length >= 5) {
                  alert("Maximum of 5 notebooks allowed in the chain.");
                }
              }}
            >
              Add to Chain
            </button>
            <button 
              className={localStyles.primaryBtn} 
              onClick={handleSaveChain}
              disabled={savingChain}
              style={{ marginLeft: 'auto' }}
            >
              {savingChain ? "Saving..." : "Save Configuration"}
            </button>
          </div>
        </div>
      </section>

      <section className={styles.infoCard}>
        <div className={styles.cardTitle}>
          <h3>Query History</h3>
          <button 
            className={localStyles.secondaryBtn} 
            onClick={() => fetchData()}
            style={{ padding: '6px 12px', fontSize: '0.8rem' }}
          >
            Refresh
          </button>
        </div>
        <div className={localStyles.historyTable}>
          <table>
            <thead>
              <tr>
                <th>Notebook</th>
                <th>Question</th>
                <th>Source</th>
                <th>Date</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {history.map(h => (
                <tr key={h.id} className={localStyles.historyRow}>
                  <td>{h.notebook_title}</td>
                  <td className={localStyles.qCell}>{h.question}</td>
                  <td><span className={h.source === "telegram" ? localStyles.tgBadge : localStyles.dbBadge}>{h.source}</span></td>
                  <td>{new Date(h.created_at).toLocaleString()}</td>
                  <td>
                    <button 
                      className={localStyles.secondaryBtn}
                      onClick={() => setSelectedHistory(h)}
                      style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* History Modal */}
      {selectedHistory && (
        <div className={localStyles.modalOverlay} onClick={() => setSelectedHistory(null)}>
          <div className={localStyles.modalContent} onClick={e => e.stopPropagation()}>
            <div className={localStyles.modalHeader}>
              <h3>Query Details</h3>
              <button className={localStyles.closeBtn} onClick={() => setSelectedHistory(null)}>✕</button>
            </div>
            <div className={localStyles.modalBody}>
              <div className={localStyles.detailGroup}>
                <span className={localStyles.detailLabel}>Question:</span>
                <p className={localStyles.detailValue}>{selectedHistory.question}</p>
              </div>
              <div className={localStyles.detailGroup}>
                <span className={localStyles.detailLabel}>Answer:</span>
                <div className={localStyles.markdownBody} style={{ marginTop: '4px' }}>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {formatAnswer(selectedHistory.answer)}
                  </ReactMarkdown>
                </div>
              </div>
              <div className={localStyles.detailGroup} style={{ display: 'flex', gap: '20px', marginTop: '10px' }}>
                <div>
                  <span className={localStyles.detailLabel}>Notebook:</span>
                  <span style={{ fontSize: '0.9rem', color: '#fff' }}>{selectedHistory.notebook_title}</span>
                </div>
                <div>
                  <span className={localStyles.detailLabel}>Source:</span>
                  <span className={selectedHistory.source === "telegram" ? localStyles.tgBadge : localStyles.dbBadge}>{selectedHistory.source}</span>
                </div>
                <div>
                  <span className={localStyles.detailLabel}>Date:</span>
                  <span style={{ fontSize: '0.9rem', color: 'var(--text-dim)' }}>{new Date(selectedHistory.created_at).toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
