declare module 'better-sqlite3' {
  interface Database {
    exec(sql: string): void;
    prepare(sql: string): Statement;
    close(): void;
  }

  interface Statement {
    run(...params: unknown[]): { changes: number };
    get(...params: unknown[]): Record<string, unknown> | undefined;
    all(...params: unknown[]): Record<string, unknown>[];
    finalize(): void;
  }

  interface BetterSqlite3Constructor {
    new (filename: string, options?: unknown): Database;
    (filename: string, options?: unknown): Database;
  }

  const BetterSqlite3: BetterSqlite3Constructor;

  export default BetterSqlite3;
}
