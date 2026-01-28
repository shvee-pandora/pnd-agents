'use client';

import { useEffect, useState } from 'react';
import { AgentCard } from './AgentCard';
import styles from './AgentGrid.module.css';

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

interface AgentListResponse {
  agents: AgentSummary[];
  total: number;
}

export function AgentGrid() {
  const [agents, setAgents] = useState<AgentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchAgents() {
      try {
        const response = await fetch('/api/agents');
        if (!response.ok) {
          throw new Error('Failed to fetch agents');
        }
        const data: AgentListResponse = await response.json();
        setAgents(data.agents);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    }

    fetchAgents();
  }, []);

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner} />
        <p>Loading agents...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.error}>
        <p>Error: {error}</p>
        <p className={styles.hint}>Make sure the API server is running on port 8000</p>
      </div>
    );
  }

  if (agents.length === 0) {
    return (
      <div className={styles.empty}>
        <p>No agents found</p>
      </div>
    );
  }

  return (
    <div className={styles.grid}>
      {agents.map((agent) => (
        <AgentCard key={agent.id} agent={agent} />
      ))}
    </div>
  );
}
