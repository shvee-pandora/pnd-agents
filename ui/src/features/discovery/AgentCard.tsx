import styles from './AgentCard.module.css';

interface AgentSummary {
  id: string;
  name: string;
  description: string;
  version: string;
  category: string | null;
  icon: string | null;
  status: string;
  tags: string[];
}

interface AgentCardProps {
  agent: AgentSummary;
}

const statusColors: Record<string, string> = {
  stable: '#22c55e',
  beta: '#f59e0b',
  experimental: '#ef4444',
  deprecated: '#6b7280',
};

export function AgentCard({ agent }: AgentCardProps) {
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div className={styles.icon}>
          {agent.icon || agent.name.charAt(0)}
        </div>
        <div className={styles.meta}>
          <h3 className={styles.name}>{agent.name}</h3>
          <span className={styles.version}>v{agent.version}</span>
        </div>
      </div>
      <p className={styles.description}>{agent.description}</p>
      <div className={styles.footer}>
        <div className={styles.tags}>
          {agent.category && (
            <span className={styles.category}>{agent.category}</span>
          )}
          <span
            className={styles.status}
            style={{ backgroundColor: statusColors[agent.status] || '#6b7280' }}
          >
            {agent.status}
          </span>
        </div>
        <button className={styles.runButton}>Run</button>
      </div>
    </div>
  );
}
