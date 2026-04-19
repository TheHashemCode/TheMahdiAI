"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";
import styles from "./Shell.module.css";

const HomeIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
);

const UsersIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
);

const ChatIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
);

const SettingsIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
);

export default function Shell({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  const navItems = [
    { label: "Overview", icon: <HomeIcon />, path: "/" },
    { label: "Users", icon: <UsersIcon />, path: "/users" },
    { label: "Sessions", icon: <ChatIcon />, path: "/sessions" },
    { label: "Settings", icon: <SettingsIcon />, path: "/settings" },
  ];

  return (
    <div className={styles.wrapper}>
      <div className={styles.bgGlow} />

      <aside className={styles.sidebar}>
        <div className={styles.brand}>
          <div className={styles.logoBox}>
            <span className={styles.logoLetter}>M</span>
          </div>
          <div className={styles.brandInfo}>
            <span className={styles.brandName}>TheMahdiAI</span>
            <span className={styles.brandTag}>Admin Console</span>
          </div>
        </div>

        <div className={styles.navGroup}>
          <div className={styles.navHeader}>MAIN MENU</div>
          {navItems.map((item) => (
            <Link
              key={item.path}
              href={item.path}
              className={`${styles.navLink} ${pathname === item.path ? styles.active : ""}`}
            >
              <span className={styles.navIcon}>{item.icon}</span>
              {item.label}
              {pathname === item.path && <div className={styles.activePill} />}
            </Link>
          ))}
        </div>

        <div className={styles.sidebarFooter}>
          <div className={styles.statusBadge}>
            <span className={styles.statusDot} />
            System Live
          </div>
        </div>
      </aside>

      <main className={styles.mainContent}>
        <header className={styles.pageHeader}>
          <div className={styles.breadcrumbs}>
            <span className={styles.bcRoot}>Admin</span>
            <span className={styles.bcSep}>/</span>
            <span className={styles.bcCurrent}>
              {navItems.find((n) => n.path === pathname)?.label || "Dashboard"}
            </span>
          </div>
          <div className={styles.avatar}>AD</div>
        </header>

        <div className="fade-in">{children}</div>
      </main>
    </div>
  );
}
