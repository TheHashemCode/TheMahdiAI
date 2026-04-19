"use client";

import { useEffect, useState } from "react";
import { API_BASE_URL } from "@/lib/constants";
import Link from "next/link";
import s from "./page.module.css";

interface Session {
  id: string;
  username: string;
  is_active: boolean;
  total_tokens: number;
  created_at: string;
  context_window: any[];
}

export default function SessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    fetch(`${API_BASE_URL}/admin/sessions`)
      .then((res) => res.json())
      .then((data) => { setSessions(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  if (!mounted) return null;

  return (
    <div className={s.card}>
      <div className={s.tableHeader}>
        <h3>Chat Sessions</h3>
        <p>Monitor real-time AI conversations. Select a session to view history.</p>
      </div>
      <div className={s.tableWrap}>
        <table>
          <thead>
            <tr>
              <th>User</th>
              <th>Status</th>
              <th>Tokens</th>
              <th>Messages</th>
              <th>Started</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className={s.emptyCell}>Syncing sessions...</td></tr>
            ) : sessions.length === 0 ? (
              <tr><td colSpan={6} className={s.emptyCell}>No sessions found.</td></tr>
            ) : (
              sessions.map((session) => (
                <tr key={session.id}>
                  <td>@{session.username}</td>
                  <td>
                    <span className={`badge ${session.is_active ? "badge-success" : "badge-warning"}`}>
                      {session.is_active ? "Active" : "Archived"}
                    </span>
                  </td>
                  <td>{session.total_tokens}</td>
                  <td>{session.context_window?.length || 0}</td>
                  <td>{new Date(session.created_at).toLocaleString()}</td>
                  <td>
                    <Link href={`/sessions/${session.id}`} className={s.btnView}>
                      View History
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
