// Plasma Engine API Types

// =============================================================================
// AUTHENTICATION & USER MANAGEMENT (Gateway Service)
// =============================================================================

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: UserRole;
  organizationId: string;
  avatar?: string;
  createdAt: string;
  updatedAt: string;
}

export type UserRole = 'admin' | 'editor' | 'viewer' | 'api_user';

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
}

export interface RefreshTokenRequest {
  refreshToken: string;
}

// =============================================================================
// RESEARCH SERVICE
// =============================================================================

export interface Document {
  id: string;
  title: string;
  content: string;
  type: DocumentType;
  uploadedBy: string;
  uploadedAt: string;
  fileSize: number;
  processingStatus: ProcessingStatus;
  vectorEmbeddings?: number[];
  metadata: DocumentMetadata;
}

export type DocumentType = 'pdf' | 'txt' | 'docx' | 'md' | 'html';
export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface DocumentMetadata {
  author?: string;
  createdDate?: string;
  language?: string;
  wordCount: number;
  pageCount?: number;
  tags: string[];
}

export interface SearchRequest {
  query: string;
  limit?: number;
  threshold?: number;
  filters?: SearchFilters;
}

export interface SearchFilters {
  documentType?: DocumentType[];
  dateRange?: {
    start: string;
    end: string;
  };
  tags?: string[];
  author?: string;
}

export interface SearchResult {
  document: Document;
  score: number;
  relevantChunks: ChunkResult[];
}

export interface ChunkResult {
  text: string;
  score: number;
  startIndex: number;
  endIndex: number;
}

export interface KnowledgeGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'concept' | 'entity' | 'document';
  properties: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  weight: number;
}

// =============================================================================
// BRAND SERVICE
// =============================================================================

export interface BrandMention {
  id: string;
  content: string;
  author: string;
  authorFollowers: number;
  platform: SocialPlatform;
  url: string;
  publishedAt: string;
  sentiment: SentimentAnalysis;
  engagement: EngagementMetrics;
  brandKeywords: string[];
  location?: string;
  language: string;
}

export type SocialPlatform = 'twitter' | 'instagram' | 'linkedin' | 'reddit' | 'facebook';

export interface SentimentAnalysis {
  overall: SentimentScore;
  aspects: AspectSentiment[];
  confidence: number;
  emotions: EmotionAnalysis;
}

export interface SentimentScore {
  label: 'positive' | 'neutral' | 'negative';
  score: number; // -1 to 1
}

export interface AspectSentiment {
  aspect: string;
  sentiment: SentimentScore;
}

export interface EmotionAnalysis {
  joy: number;
  anger: number;
  fear: number;
  sadness: number;
  surprise: number;
  disgust: number;
}

export interface EngagementMetrics {
  likes: number;
  shares: number;
  comments: number;
  retweets?: number; // Twitter specific
  replies?: number;
}

export interface BrandAnalytics {
  totalMentions: number;
  sentimentDistribution: {
    positive: number;
    neutral: number;
    negative: number;
  };
  engagementRate: number;
  reach: number;
  impressions: number;
  topKeywords: KeywordMetric[];
  timeSeriesData: TimeSeriesPoint[];
  competitorComparison?: CompetitorMetric[];
}

export interface KeywordMetric {
  keyword: string;
  mentions: number;
  sentiment: number;
  trend: 'rising' | 'falling' | 'stable';
}

export interface TimeSeriesPoint {
  timestamp: string;
  mentions: number;
  sentiment: number;
  engagement: number;
}

export interface CompetitorMetric {
  name: string;
  mentions: number;
  sentiment: number;
  shareOfVoice: number;
}

export interface AlertRule {
  id: string;
  name: string;
  keywords: string[];
  platforms: SocialPlatform[];
  sentimentThreshold?: number;
  volumeThreshold?: number;
  isActive: boolean;
  notifications: NotificationChannel[];
}

export type NotificationChannel = 'email' | 'slack' | 'webhook';

// =============================================================================
// CONTENT SERVICE
// =============================================================================

export interface ContentPiece {
  id: string;
  title: string;
  content: string;
  type: ContentType;
  status: ContentStatus;
  brandVoice: string;
  targetAudience: string[];
  platforms: SocialPlatform[];
  scheduledFor?: string;
  publishedAt?: string;
  metrics?: ContentMetrics;
  tags: string[];
  authorId: string;
  createdAt: string;
  updatedAt: string;
}

export type ContentType = 'blog_post' | 'social_post' | 'email' | 'ad_copy' | 'press_release';
export type ContentStatus = 'draft' | 'review' | 'approved' | 'scheduled' | 'published' | 'archived';

export interface ContentMetrics {
  views: number;
  clicks: number;
  shares: number;
  likes: number;
  comments: number;
  conversions: number;
  engagementRate: number;
}

export interface BrandVoice {
  id: string;
  name: string;
  description: string;
  tone: string[];
  keywords: string[];
  avoidWords: string[];
  examples: string[];
  isDefault: boolean;
}

export interface ContentCalendar {
  id: string;
  name: string;
  entries: CalendarEntry[];
}

export interface CalendarEntry {
  id: string;
  contentId: string;
  scheduledDate: string;
  platforms: SocialPlatform[];
  status: 'scheduled' | 'published' | 'failed';
}

export interface ContentGenRequest {
  type: ContentType;
  prompt: string;
  brandVoice: string;
  targetAudience: string[];
  platforms: SocialPlatform[];
  maxLength?: number;
  tone?: string;
  includeCTA?: boolean;
}

export interface ContentGenResponse {
  content: string;
  alternatives: string[];
  metadata: {
    wordCount: number;
    estimatedReadTime: number;
    tone: string;
    sentiment: number;
  };
}

// =============================================================================
// AGENT SERVICE
// =============================================================================

export interface Agent {
  id: string;
  name: string;
  description: string;
  type: AgentType;
  status: AgentStatus;
  configuration: AgentConfig;
  workflows: Workflow[];
  metrics: AgentMetrics;
  createdAt: string;
  updatedAt: string;
}

export type AgentType = 'research' | 'content' | 'social' | 'analytics' | 'automation' | 'custom';
export type AgentStatus = 'idle' | 'running' | 'paused' | 'error' | 'stopped';

export interface AgentConfig {
  model: string;
  temperature: number;
  maxTokens: number;
  tools: ToolConfig[];
  memory: MemoryConfig;
  triggers: TriggerConfig[];
}

export interface ToolConfig {
  name: string;
  type: 'search' | 'calculator' | 'browser' | 'api' | 'custom';
  configuration: Record<string, any>;
  enabled: boolean;
}

export interface MemoryConfig {
  type: 'buffer' | 'window' | 'summary';
  maxTokens: number;
  summaryPrompt?: string;
}

export interface TriggerConfig {
  type: 'schedule' | 'webhook' | 'event';
  configuration: Record<string, any>;
  enabled: boolean;
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
  status: WorkflowStatus;
  schedule?: ScheduleConfig;
  lastRun?: WorkflowRun;
  createdAt: string;
  updatedAt: string;
}

export type WorkflowStatus = 'draft' | 'active' | 'paused' | 'archived';

export interface WorkflowStep {
  id: string;
  name: string;
  type: StepType;
  configuration: Record<string, any>;
  dependencies: string[];
  conditions?: StepCondition[];
}

export type StepType = 'llm_call' | 'api_request' | 'data_transform' | 'condition' | 'loop' | 'browser_action';

export interface StepCondition {
  field: string;
  operator: 'equals' | 'not_equals' | 'contains' | 'greater_than' | 'less_than';
  value: any;
}

export interface ScheduleConfig {
  type: 'cron' | 'interval';
  expression: string;
  timezone: string;
}

export interface WorkflowRun {
  id: string;
  workflowId: string;
  status: RunStatus;
  startedAt: string;
  completedAt?: string;
  error?: string;
  results: StepResult[];
  metrics: RunMetrics;
}

export type RunStatus = 'running' | 'completed' | 'failed' | 'cancelled';

export interface StepResult {
  stepId: string;
  status: RunStatus;
  output: any;
  error?: string;
  duration: number;
}

export interface RunMetrics {
  duration: number;
  tokensUsed: number;
  apiCalls: number;
  cost: number;
}

export interface AgentMetrics {
  totalRuns: number;
  successRate: number;
  avgDuration: number;
  totalTokens: number;
  totalCost: number;
  lastActivity: string;
}

// =============================================================================
// SHARED TYPES
// =============================================================================

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: ApiError;
  meta?: ResponseMeta;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

export interface ResponseMeta {
  page?: number;
  limit?: number;
  total?: number;
  hasMore?: boolean;
}

export interface PaginationRequest {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasMore: boolean;
  };
}

// WebSocket Events
export interface WebSocketEvent {
  type: string;
  payload: any;
  timestamp: string;
}

export interface ServiceStatus {
  name: string;
  status: 'healthy' | 'unhealthy' | 'degraded';
  responseTime: number;
  lastCheck: string;
  version: string;
}

export interface SystemHealth {
  services: ServiceStatus[];
  overall: 'healthy' | 'unhealthy' | 'degraded';
}