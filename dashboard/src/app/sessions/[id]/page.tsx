"use client";

import { useEffect, useState, use } from "react";
import { API_BASE_URL } from "@/lib/constants";
import Link from "next/link";
import s from "./details.module.css";

interface Session {
  id: string;
  username: string;
  is_active: boolean;
  total_tokens: number;
  created_at: string;
  context_window: { role: string; content: string }[];
}

export default function SessionDetailsPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const sessionId = resolvedParams.id;
  
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    fetch(`${API_BASE_URL}/admin/sessions`)
      .then((res) => res.json())
      .then((data: Session[]) => {
        const found = data.find(s => s.id === sessionId);
        setSession(found || null);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [sessionId]);

  if (!mounted) return null;
  if (loading) return <div className={s.loading}>Loading conversation...</div>;
  if (!session) return <div className={s.error}>Session not found.</div>;

  return (
    <div className={s.pageWrapper}>
      <header className={s.chatHeader}>
        <div className={s.headerLeft}>
          <Link href="/sessions" className={s.btnBack}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
            Back to Sessions
          </Link>
          <div className={s.sessionTitle}>
            <h2>Conversation with @{session.username}</h2>
            <div className={s.metaPills}>
              <span className="badge badge-info">{session.total_tokens} tokens</span>
              <span className={`badge ${session.is_active ? "badge-success" : "badge-warning"}`}>
                {session.is_active ? "Active Session" : "Archived"}
              </span>
            </div>
          </div>
        </div>
      </header>

      <div className={s.chatScroll}>
        <div className={s.chatContainer}>
          {session.context_window && session.context_window.length > 0 ? (
            session.context_window.filter(m => m.role !== 'system').map((msg, idx) => (
              <div key={idx} className={`${s.messageRow} ${msg.role === 'user' ? s.userRow : s.assistantRow}`}>
                <div className={s.msgMeta}>
                  <span className={s.roleLabel}>{msg.role}</span>
                </div>
                <div className={`${s.bubble} ${msg.role === 'user' ? s.userBubble : s.assistantBubble}`}>
                  {msg.content}
                </div>
              </div>
            ))
          ) : (
            <div className={s.emptyState}>No message history available for this session.</div>
          )}
        </div>
      </div>
    </div>
  );
}
