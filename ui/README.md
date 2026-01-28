# PND Agents Marketplace UI

Next.js-based frontend for the PND Agents Marketplace.

## Overview

This is the marketplace UI where engineers can discover agents, understand what they do, run them on repos, and see results.

## Quick Start

```bash
# From the ui/ directory
npm install

# Run the development server (requires API on port 8000)
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the marketplace.

## Features

### Phase 1 (Current)
- Agent discovery and browsing
- Category and status filtering
- Search functionality
- Agent detail view

### Future Phases
- Agent execution on repositories
- Results and logs viewer
- Meta-agent composition

## Project Structure

```
ui/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page (marketplace)
│   │   └── globals.css         # Global styles
│   ├── components/             # Shared components
│   │   └── Header.tsx
│   ├── features/               # Feature modules
│   │   ├── discovery/          # Agent catalog & search
│   │   ├── execution/          # Run agents (future)
│   │   └── results/            # Logs & output (future)
│   └── lib/                    # Utilities
│       └── api.ts              # API client
├── public/                     # Static assets
├── package.json
└── tsconfig.json
```

## API Integration

The UI proxies API requests to the FastAPI backend:

- Development: `http://localhost:8000/api/*`
- The proxy is configured in `next.config.js`

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run production server
npm start

# Lint
npm run lint
```
