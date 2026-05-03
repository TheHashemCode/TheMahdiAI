"use client";

import { useEffect, useState } from "react";
import { API_BASE_URL } from "@/lib/constants";
import Link from "next/link";
import s from "./page.module.css";

interface Stats {
  total_users: number;
  total_sessions: number;
  total_tokens_used: number;
}

export default function Home() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/admin/stats`)
      .then((res) => {
        if (!res.ok) throw new Error("Backend unreachable");
        return res.json();
      })
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className={s.overviewStack}>
      <div className={s.banner}>
        <div className={s.bannerInfo}>
          <h2>Welcome back, Admin</h2>
          <p>TheMahdiAI is currently active and monitoring user requests.</p>
        </div>
      </div>

      <div className={s.statsGrid}>
        <Link href="/users" className={s.statCard}>
          <div className={s.cardHead}>
            <span className={s.sLabel}>Total Users</span>
            <div className={`${s.sIcon} ${s.purple}`}>👤</div>
          </div>
          <div className={s.sValue}>{loading ? "–" : stats?.total_users ?? 0}</div>
          <div className={`${s.sTrend} ${s.positive}`}>↑ Registered users</div>
        </Link>

        <Link href="/sessions" className={s.statCard}>
          <div className={s.cardHead}>
            <span className={s.sLabel}>Total Sessions</span>
            <div className={`${s.sIcon} ${s.green}`}>💬</div>
          </div>
          <div className={s.sValue}>{loading ? "–" : stats?.total_sessions ?? 0}</div>
          <div className={`${s.sTrend} ${s.positive}`}>↑ Active conversations</div>
        </Link>

        <div className={s.statCard} style={{ cursor: 'default' }}>
          <div className={s.cardHead}>
            <span className={s.sLabel}>Tokens Used</span>
            <div className={`${s.sIcon} ${s.gold}`}>🧠</div>
          </div>
          <div className={s.sValue}>
            {loading ? "–" : (stats?.total_tokens_used ?? 0).toLocaleString()}
          </div>
          <div className={s.sTrend}>AI Intelligence</div>
        </div>
      </div>

      <div className={s.infoCard}>
        <div className={s.cardTitle}>
          <h3>Backend Integration</h3>
          {error ? (
            <span className={s.statusErr}>{error}</span>
          ) : (
            <span className={s.statusOk}>Connected</span>
          )}
        </div>
        <p>
          Connected to <code>{API_BASE_URL}</code>. Data synchronized via
          PostgreSQL and SQLAlchemy.
        </p>
        <div className={s.pillGroup}>
          <span className="badge badge-success">SQLModel Active</span>
          <span className="badge badge-info">LiteLLM Monitoring</span>
          <span className="badge badge-warning">Failover: OpenAI → Anthropic → Groq</span>
        </div>
      </div>
    </div>
  );
}
