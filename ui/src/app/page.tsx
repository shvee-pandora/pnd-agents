import { AgentGrid } from '@/features/discovery/AgentGrid';
import { Header } from '@/components/Header';
import { SearchBar } from '@/features/discovery/SearchBar';
import styles from './page.module.css';

export default function Home() {
  return (
    <main className={styles.main}>
      <Header />
      <div className={styles.content}>
        <div className={styles.hero}>
          <h1 className={styles.title}>PND Agents Marketplace</h1>
          <p className={styles.subtitle}>
            Discover, run, and compose AI agents for software development
          </p>
        </div>
        <SearchBar />
        <AgentGrid />
      </div>
    </main>
  );
}
