"use client";

import { useEffect, useState } from "react";
import { API_BASE_URL } from "@/lib/constants";
import s from "./page.module.css";

interface User {
  id: string;
  telegram_id: number;
  username: string;
  first_name: string;
  language: string;
  created_at: string;
  daily_token_used: number;
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    fetch(`${API_BASE_URL}/admin/users`)
      .then((res) => res.json())
      .then((data) => { setUsers(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  if (!mounted) return null;

  return (
    <div className={s.card}>
      <div className={s.tableHeader}>
        <h3>System Users</h3>
        <p>All users who have interacted with the Telegram bot.</p>
      </div>
      <div className={s.tableWrap}>
        <table>
          <thead>
            <tr>
              <th>Telegram ID</th>
              <th>Identity</th>
              <th>Language</th>
              <th>Daily Used</th>
              <th>Joined</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} className={s.emptyCell}>Syncing users...</td></tr>
            ) : users.length === 0 ? (
              <tr><td colSpan={5} className={s.emptyCell}>No users found.</td></tr>
            ) : (
              users.map((user) => (
                <tr key={user.id}>
                  <td><code>{user.telegram_id}</code></td>
                  <td>
                    <div className={s.userInfo}>
                      <span className={s.un}>@{user.username || "hidden"}</span>
                      <span className={s.fn}>{user.first_name}</span>
                    </div>
                  </td>
                  <td><span className="badge badge-info">{user.language}</span></td>
                  <td><span className={s.tokenVal}>{user.daily_token_used}</span></td>
                  <td>{new Date(user.created_at).toLocaleDateString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
