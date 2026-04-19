"use client";

import { useEffect, useState } from "react";
import { API_BASE_URL } from "@/lib/constants";
import s from "./page.module.css";

interface Config {
  key: string;
  value: string;
}

export default function SettingsPage() {
  const [configs, setConfigs] = useState<Config[]>([]);
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");
  const [saving, setSaving] = useState(false);

  // For adding new config
  const [showAdd, setShowAdd] = useState(false);
  const [newKey, setNewKey] = useState("");
  const [newValue, setNewValue] = useState("");

  const fetchConfigs = () => {
    fetch(`${API_BASE_URL}/admin/configs`)
      .then((res) => res.json())
      .then((data: Config[]) => {
        // Default keys we want to ensure are visible
        const defaultKeys = [
          { key: 'system_prompt', value: 'You are a helpful AI assistant.' },
          { key: 'max_tokens', value: '1000' },
          { key: 'max_req_per_minute', value: '20' },
          { key: 'max_req_per_day', value: '500' },
          { key: 'max_daily_tokens', value: '1000000' },
          { key: 'max_context_window', value: '32768' }
        ];

        const existingKeys = new Set(data.map(c => c.key));
        defaultKeys.forEach(dk => {
          if (!existingKeys.has(dk.key)) {
            data.push(dk);
          }
        });
        
        setConfigs(data);
      })
      .catch((err) => console.error("Failed to fetch configs", err));
  };

  useEffect(() => {
    fetchConfigs();
  }, []);

  const handleSave = async (key: string, value: string) => {
    setSaving(true);
    try {
      const res = await fetch(`${API_BASE_URL}/admin/configs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key, value }),
      });
      if (!res.ok) throw new Error();
      setEditingKey(null);
      setShowAdd(false);
      setNewKey("");
      setNewValue("");
      fetchConfigs();
    } catch (err) {
      alert("Failed to save config.");
    } finally {
      setSaving(false);
    }
  };

  const getConfigDescription = (key: string) => {
    if (key === 'system_prompt') return "The primary system instruction for AI persona and rules.";
    if (key === 'max_tokens') return "Maximum number of tokens the AI can generate in a single response.";
    if (key === 'max_req_per_minute') return "Rate limit: maximum requests allowed per minute per user.";
    if (key === 'max_req_per_day') return "Daily quota: maximum requests allowed per user per day.";
    if (key === 'max_daily_tokens') return "Daily quota: maximum total tokens allowed per user per day.";
    if (key === 'max_context_window') return "Context window: maximum tokens (history + current) sent to AI.";
    return "Custom system-wide configuration parameter.";
  };

  return (
    <div className={s.card}>
      <div className={s.header}>
        <div className={s.headerContent}>
          <h3>System Orchestration</h3>
          <p>Manage AI behaviors and system-wide configurations.</p>
        </div>
        <button className={s.btnAdd} onClick={() => setShowAdd(true)}>+ Add Config</button>
      </div>

      <div className={s.configList}>
        {showAdd && (
          <div className={`${s.configRow} ${s.newRow}`}>
            <div className={s.rowMeta}>
              <input 
                className={s.keyInput} 
                placeholder="config_key_name"
                value={newKey}
                onChange={e => setNewKey(e.target.value)}
              />
            </div>
            <div className={s.editor}>
              <textarea
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
                placeholder="Enter value..."
              />
              <div className={s.editorActions}>
                <button className={s.btnSave} onClick={() => handleSave(newKey, newValue)} disabled={saving || !newKey}>
                  {saving ? "Saving..." : "Create Configuration"}
                </button>
                <button className={s.btnCancel} onClick={() => setShowAdd(false)}>Cancel</button>
              </div>
            </div>
          </div>
        )}

        {configs.map((config) => (
          <div key={config.key} className={s.configRow}>
            <div className={s.rowMeta}>
              <span className={s.keyBadge}>{config.key}</span>
              <p className={s.keyDesc}>{getConfigDescription(config.key)}</p>
            </div>

            {editingKey === config.key ? (
              <div className={s.editor}>
                {['max_tokens', 'max_req_per_minute', 'max_req_per_day', 'max_daily_tokens', 'max_context_window'].includes(config.key) ? (
                  <input 
                    type="number"
                    className={s.numInput}
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                  />
                ) : (
                  <textarea
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    placeholder="Enter dynamic instructions..."
                  />
                )}
                <div className={s.editorActions}>
                  <button
                    className={s.btnSave}
                    onClick={() => handleSave(config.key, editValue)}
                    disabled={saving}
                  >
                    {saving ? "Deploying..." : "Update Parameter"}
                  </button>
                  <button
                    className={s.btnCancel}
                    onClick={() => setEditingKey(null)}
                  >
                    Discard
                  </button>
                </div>
              </div>
            ) : (
              <div className={s.preview}>
                <div className={s.previewText}>
                  {['max_tokens', 'max_req_per_minute', 'max_req_per_day', 'max_daily_tokens', 'max_context_window'].includes(config.key) ? 
                    <strong>{config.value} {config.key.includes('tokens') ? 'tokens' : 'units'}</strong> : 
                    config.value
                  }
                </div>
                <button
                  className={s.btnEdit}
                  onClick={() => {
                    setEditingKey(config.key);
                    setEditValue(config.value);
                  }}
                >
                  Edit Setting
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
