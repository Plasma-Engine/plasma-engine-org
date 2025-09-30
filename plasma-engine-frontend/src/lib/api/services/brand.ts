import { brandApi } from '../client';
import { 
  BrandMention, 
  BrandAnalytics, 
  AlertRule,
  SocialPlatform,
  ApiResponse,
  PaginatedResponse,
  PaginationRequest
} from '../types';

export class BrandService {
  // Brand Mentions
  async getBrandMentions(params?: PaginationRequest & {
    platforms?: SocialPlatform[];
    sentiment?: 'positive' | 'neutral' | 'negative';
    dateRange?: { start: string; end: string };
    keywords?: string[];
  }): Promise<ApiResponse<PaginatedResponse<BrandMention>>> {
    return brandApi.get('/mentions', { params });
  }

  async getBrandMention(id: string): Promise<ApiResponse<BrandMention>> {
    return brandApi.get(`/mentions/${id}`);
  }

  async updateMentionSentiment(id: string, sentiment: {
    overall: { label: 'positive' | 'neutral' | 'negative'; score: number };
  }): Promise<ApiResponse<BrandMention>> {
    return brandApi.patch(`/mentions/${id}/sentiment`, sentiment);
  }

  async archiveMention(id: string): Promise<ApiResponse<void>> {
    return brandApi.post(`/mentions/${id}/archive`);
  }

  async flagMention(id: string, reason: string): Promise<ApiResponse<void>> {
    return brandApi.post(`/mentions/${id}/flag`, { reason });
  }

  // Real-time Monitoring
  async startTwitterCollection(keywords: string[]): Promise<ApiResponse<{ 
    collectionId: string; 
    status: string; 
  }>> {
    return brandApi.post('/collect/twitter/start', { keywords });
  }

  async stopTwitterCollection(collectionId: string): Promise<ApiResponse<void>> {
    return brandApi.post(`/collect/twitter/${collectionId}/stop`);
  }

  async getCollectionStatus(collectionId: string): Promise<ApiResponse<{
    id: string;
    status: 'running' | 'stopped' | 'error';
    keywords: string[];
    startedAt: string;
    stoppedAt?: string;
    mentionsCollected: number;
    lastMentionAt?: string;
  }>> {
    return brandApi.get(`/collect/${collectionId}/status`);
  }

  // Analytics & Insights
  async getBrandAnalytics(params?: {
    timeRange?: '24h' | '7d' | '30d' | '90d' | 'custom';
    startDate?: string;
    endDate?: string;
    platforms?: SocialPlatform[];
    keywords?: string[];
  }): Promise<ApiResponse<BrandAnalytics>> {
    return brandApi.get('/analytics', { params });
  }

  async getSentimentTrends(params?: {
    timeRange?: '24h' | '7d' | '30d' | '90d';
    granularity?: 'hour' | 'day' | 'week';
    platforms?: SocialPlatform[];
  }): Promise<ApiResponse<Array<{
    timestamp: string;
    sentiment: { positive: number; neutral: number; negative: number };
    volume: number;
  }>>> {
    return brandApi.get('/analytics/sentiment-trends', { params });
  }

  async getTopInfluencers(params?: {
    timeRange?: '24h' | '7d' | '30d';
    platforms?: SocialPlatform[];
    minFollowers?: number;
    limit?: number;
  }): Promise<ApiResponse<Array<{
    author: string;
    platform: SocialPlatform;
    followers: number;
    mentions: number;
    averageSentiment: number;
    reach: number;
    engagementRate: number;
  }>>> {
    return brandApi.get('/analytics/influencers', { params });
  }

  async getCompetitorAnalysis(competitors: string[], params?: {
    timeRange?: '24h' | '7d' | '30d';
    platforms?: SocialPlatform[];
  }): Promise<ApiResponse<Array<{
    competitor: string;
    mentions: number;
    sentiment: number;
    shareOfVoice: number;
    engagement: number;
    trends: Array<{
      timestamp: string;
      mentions: number;
      sentiment: number;
    }>;
  }>>> {
    return brandApi.post('/analytics/competitors', { competitors, ...params });
  }

  async getEmotionAnalysis(params?: {
    timeRange?: '24h' | '7d' | '30d';
    platforms?: SocialPlatform[];
  }): Promise<ApiResponse<{
    emotions: {
      joy: number;
      anger: number;
      fear: number;
      sadness: number;
      surprise: number;
      disgust: number;
    };
    trends: Array<{
      timestamp: string;
      emotions: {
        joy: number;
        anger: number;
        fear: number;
        sadness: number;
        surprise: number;
        disgust: number;
      };
    }>;
  }>> {
    return brandApi.get('/analytics/emotions', { params });
  }

  // Keywords & Topics
  async getKeywordAnalysis(params?: {
    timeRange?: '24h' | '7d' | '30d';
    platforms?: SocialPlatform[];
    limit?: number;
  }): Promise<ApiResponse<Array<{
    keyword: string;
    mentions: number;
    sentiment: number;
    trend: 'rising' | 'falling' | 'stable';
    trendPercentage: number;
    associatedTerms: string[];
  }>>> {
    return brandApi.get('/analytics/keywords', { params });
  }

  async getTopicClusters(params?: {
    timeRange?: '24h' | '7d' | '30d';
    platforms?: SocialPlatform[];
    minClusterSize?: number;
  }): Promise<ApiResponse<Array<{
    id: string;
    label: string;
    keywords: string[];
    mentions: number;
    sentiment: number;
    centroid: number[];
  }>>> {
    return brandApi.get('/analytics/topics', { params });
  }

  // Alerts & Notifications
  async getAlertRules(): Promise<ApiResponse<AlertRule[]>> {
    return brandApi.get('/alerts/rules');
  }

  async createAlertRule(data: Omit<AlertRule, 'id'>): Promise<ApiResponse<AlertRule>> {
    return brandApi.post('/alerts/rules', data);
  }

  async updateAlertRule(id: string, data: Partial<AlertRule>): Promise<ApiResponse<AlertRule>> {
    return brandApi.patch(`/alerts/rules/${id}`, data);
  }

  async deleteAlertRule(id: string): Promise<ApiResponse<void>> {
    return brandApi.delete(`/alerts/rules/${id}`);
  }

  async getAlertHistory(params?: PaginationRequest & {
    ruleId?: string;
    severity?: 'low' | 'medium' | 'high' | 'critical';
    dateRange?: { start: string; end: string };
  }): Promise<ApiResponse<PaginatedResponse<{
    id: string;
    ruleId: string;
    ruleName: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    message: string;
    mentionId?: string;
    triggeredAt: string;
    acknowledgedAt?: string;
    acknowledgedBy?: string;
  }>>> {
    return brandApi.get('/alerts/history', { params });
  }

  async acknowledgeAlert(alertId: string): Promise<ApiResponse<void>> {
    return brandApi.post(`/alerts/${alertId}/acknowledge`);
  }

  // Export & Reporting
  async exportMentions(params: {
    format: 'csv' | 'xlsx' | 'json';
    dateRange: { start: string; end: string };
    platforms?: SocialPlatform[];
    sentiment?: 'positive' | 'neutral' | 'negative';
    includeMetrics?: boolean;
  }): Promise<ApiResponse<{ downloadUrl: string; expiresAt: string }>> {
    return brandApi.post('/export/mentions', params);
  }

  async generateReport(data: {
    type: 'weekly' | 'monthly' | 'quarterly' | 'custom';
    dateRange: { start: string; end: string };
    includeCompetitors?: boolean;
    competitors?: string[];
    format: 'pdf' | 'html';
    sections: Array<'summary' | 'sentiment' | 'volume' | 'influencers' | 'keywords' | 'competitors'>;
  }): Promise<ApiResponse<{ reportId: string }>> {
    return brandApi.post('/reports/generate', data);
  }

  async getReportStatus(reportId: string): Promise<ApiResponse<{
    id: string;
    status: 'pending' | 'generating' | 'completed' | 'failed';
    progress: number;
    downloadUrl?: string;
    error?: string;
    createdAt: string;
    completedAt?: string;
  }>> {
    return brandApi.get(`/reports/${reportId}/status`);
  }

  async getReports(params?: PaginationRequest): Promise<ApiResponse<PaginatedResponse<{
    id: string;
    type: string;
    dateRange: { start: string; end: string };
    status: 'pending' | 'generating' | 'completed' | 'failed';
    downloadUrl?: string;
    createdAt: string;
    completedAt?: string;
  }>>> {
    return brandApi.get('/reports', { params });
  }

  async deleteReport(reportId: string): Promise<ApiResponse<void>> {
    return brandApi.delete(`/reports/${reportId}`);
  }

  // Platform Integration
  async connectTwitter(credentials: {
    bearerToken: string;
  }): Promise<ApiResponse<{ connected: boolean; accountInfo: any }>> {
    return brandApi.post('/platforms/twitter/connect', credentials);
  }

  async disconnectTwitter(): Promise<ApiResponse<void>> {
    return brandApi.post('/platforms/twitter/disconnect');
  }

  async getPlatformStatus(): Promise<ApiResponse<{
    twitter: { connected: boolean; rateLimitRemaining: number; resetAt?: string };
    instagram: { connected: boolean; rateLimitRemaining: number; resetAt?: string };
    linkedin: { connected: boolean; rateLimitRemaining: number; resetAt?: string };
    reddit: { connected: boolean; rateLimitRemaining: number; resetAt?: string };
  }>> {
    return brandApi.get('/platforms/status');
  }
}

export const brandService = new BrandService();