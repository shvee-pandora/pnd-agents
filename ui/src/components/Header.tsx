import styles from './Header.module.css';

export function Header() {
  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <div className={styles.logo}>
          <span className={styles.logoIcon}>P</span>
          <span className={styles.logoText}>PND Agents</span>
        </div>
        <nav className={styles.nav}>
          <a href="/" className={styles.navLink}>Marketplace</a>
          <a href="/docs" className={styles.navLink}>Docs</a>
        </nav>
      </div>
    </header>
  );
}
