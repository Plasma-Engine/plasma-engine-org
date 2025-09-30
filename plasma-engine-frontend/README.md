# 🚀 Plasma Engine Frontend

> **Beautiful, Professional React Frontend for the Plasma Engine AI Platform**

[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)
[![Mantine](https://img.shields.io/badge/Mantine-7.0-339af0)](https://mantine.dev/)
[![License](https://img.shields.io/badge/License-Proprietary-red)](#)

Enterprise-grade frontend interface for the Plasma Engine AI platform, providing intuitive access to research automation, brand intelligence, content orchestration, and agent management.

## ✨ Features

### 🎨 **Professional UI/UX**
- **Mantine UI Library**: Premium React components with beautiful, professional design
- **Dark/Light Mode**: Automatic theme switching with custom Plasma Engine branding
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Smooth Animations**: Framer Motion animations for enhanced user experience

### 🔐 **Authentication & Security**
- **JWT Authentication**: Secure token-based authentication with automatic refresh
- **Role-Based Access Control**: Admin, Editor, Viewer, and API User roles
- **Session Management**: Persistent login with secure token storage
- **Multi-factor Auth Ready**: Prepared for MFA integration

### 📊 **Service Dashboards**

#### Research Service UI
- **Document Management**: Upload, organize, and search documents
- **Vector Search**: Semantic search with relevance scoring
- **Knowledge Graph**: Interactive visualization of entity relationships
- **Document Processing**: Real-time processing status and analytics

#### Brand Monitoring UI
- **Social Mentions**: Real-time Twitter, LinkedIn, Reddit monitoring
- **Sentiment Analysis**: Advanced sentiment and emotion analysis
- **Analytics Dashboard**: Comprehensive brand analytics and trends
- **Alert System**: Configurable alerts for brand mentions

#### Content Generation UI
- **AI Content Creation**: GPT-5 powered content generation
- **Brand Voice Management**: Consistent brand voice across content
- **Content Calendar**: Schedule and manage content publishing
- **Multi-platform Publishing**: Twitter, LinkedIn, Medium integration

#### Agent Orchestration UI
- **Workflow Builder**: Visual drag-and-drop workflow creation
- **Agent Management**: Deploy and monitor AI agents
- **Browser Automation**: Control and monitor browser-based tasks
- **Performance Analytics**: Track agent performance and costs

### 🛠️ **Technical Features**
- **Real-time Updates**: WebSocket integration for live data
- **API Integration**: Comprehensive REST API client with error handling
- **State Management**: Zustand for efficient state management
- **Query Caching**: TanStack Query for optimized data fetching
- **Type Safety**: Full TypeScript coverage with strict types

## 🏗️ Architecture

```
src/
├── app/                    # Next.js App Router pages
│   ├── auth/              # Authentication pages
│   ├── dashboard/         # Main application dashboard
│   └── layout.tsx         # Root layout with providers
├── lib/
│   ├── api/               # API client and service integrations
│   │   ├── client.ts      # Base API client with interceptors
│   │   ├── types.ts       # TypeScript type definitions
│   │   └── services/      # Service-specific API methods
│   ├── stores/            # Zustand state management
│   ├── hooks/             # Custom React hooks
│   └── utils/             # Utility functions
├── components/            # Reusable UI components
│   ├── ui/               # Base UI components
│   ├── charts/           # Data visualization components
│   └── forms/            # Form components
└── styles/               # Global styles and themes
```

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18.17 or later
- **npm** 9.0 or later
- **Backend Services** running (Plasma Engine services)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/plasma-engine-frontend.git
cd plasma-engine-frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Configure environment variables
# Edit .env.local with your API endpoints
```

### Environment Variables

```bash
# API Endpoints
NEXT_PUBLIC_GATEWAY_URL=http://localhost:8000
NEXT_PUBLIC_RESEARCH_URL=http://localhost:8001
NEXT_PUBLIC_BRAND_URL=http://localhost:8002
NEXT_PUBLIC_CONTENT_URL=http://localhost:8003
NEXT_PUBLIC_AGENT_URL=http://localhost:8004

# Optional: Analytics and monitoring
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn
NEXT_PUBLIC_GA_TRACKING_ID=your-ga-id
```

### Development

```bash
# Start development server
npm run dev

# Open browser
open http://localhost:3000
```

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## 📚 API Integration

The frontend connects to 5 backend services:

### Service Endpoints

| Service | Port | Purpose |
|---------|------|---------|
| Gateway | 8000 | Authentication, user management, GraphQL federation |
| Research | 8001 | Document processing, vector search, knowledge graphs |
| Brand | 8002 | Social monitoring, sentiment analysis, brand analytics |
| Content | 8003 | AI content generation, publishing, brand voice |
| Agent | 8004 | Workflow automation, agent orchestration, browser control |

### Authentication Flow

```typescript
// Login
const { user, tokens } = await gatewayService.login(email, password);

// API calls with automatic token refresh
const documents = await researchService.getDocuments();
const mentions = await brandService.getBrandMentions();
```

### Real-time Updates

```typescript
// WebSocket connection for real-time updates
const wsManager = new WebSocketManager('ws://localhost:8000/ws');
wsManager.onMessage((event) => {
  // Handle real-time events
  if (event.type === 'brand_mention') {
    // Update UI with new mention
  }
});
```

## 🎨 UI Components

### Design System

Built with **Mantine v7** for professional, enterprise-grade UI:

- **Color Palette**: Custom Plasma Engine branding
- **Typography**: Inter font family for clean, modern text
- **Spacing**: Consistent 8px grid system  
- **Components**: 100+ pre-built, accessible components
- **Icons**: Tabler Icons for consistent iconography

### Key Components

```typescript
// Professional stat cards with animations
<StatCard
  title="Active Users"
  value={1247}
  change={{ value: 8.2, trend: 'up' }}
  icon={IconUsers}
  color="green"
  href="/dashboard/users"
/>

// Real-time charts and visualizations
<LineChart data={analyticsData}>
  <Line dataKey="requests" stroke="#2196f3" />
  <Line dataKey="users" stroke="#009688" />
</LineChart>

// Advanced data tables with filtering
<DataTable
  columns={columns}
  data={documents}
  features={['sorting', 'filtering', 'pagination']}
/>
```

## 🧪 Testing

```bash
# Run unit tests
npm run test

# Run integration tests
npm run test:integration

# Run E2E tests with Playwright
npm run test:e2e

# Generate coverage report
npm run test:coverage
```

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 📞 Support

### Getting Help

- **Issues**: GitHub Issues for bugs and features
- **Discussions**: GitHub Discussions for questions
- **Email**: support@plasmaengine.com

## 📄 License

Copyright © 2025 Plasma Engine. All rights reserved.

---

Built with ❤️ by the Plasma Engine Team
