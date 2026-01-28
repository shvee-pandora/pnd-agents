'use client';

import { useState } from 'react';
import styles from './SearchBar.module.css';

export function SearchBar() {
  const [search, setSearch] = useState('');

  return (
    <div className={styles.container}>
      <div className={styles.searchWrapper}>
        <svg
          className={styles.searchIcon}
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.3-4.3" />
        </svg>
        <input
          type="text"
          placeholder="Search agents..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className={styles.input}
        />
      </div>
      <div className={styles.filters}>
        <select className={styles.select}>
          <option value="">All Categories</option>
          <option value="Development">Development</option>
          <option value="Quality">Quality</option>
          <option value="Security">Security</option>
          <option value="Analytics">Analytics</option>
        </select>
        <select className={styles.select}>
          <option value="">All Status</option>
          <option value="stable">Stable</option>
          <option value="beta">Beta</option>
          <option value="experimental">Experimental</option>
        </select>
      </div>
    </div>
  );
}
