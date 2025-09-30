import { contentApi } from '../client';
import { 
  ContentPiece, 
  BrandVoice, 
  ContentCalendar,
  ContentGenRequest,
  ContentGenResponse,
  ApiResponse,
  PaginatedResponse,
  PaginationRequest,
  SocialPlatform
} from '../types';

export class ContentService {
  // Content Management
  async getContent(params?: PaginationRequest & {
    type?: string;
    status?: string;
    brandVoice?: string;
    platforms?: SocialPlatform[];
    dateRange?: { start: string; end: string };
    tags?: string[];
  }): Promise<ApiResponse<PaginatedResponse<ContentPiece>>> {
    return contentApi.get('/content', { params });
  }

  async getContentPiece(id: string): Promise<ApiResponse<ContentPiece>> {
    return contentApi.get(`/content/${id}`);
  }

  async createContent(data: Omit<ContentPiece, 'id' | 'createdAt' | 'updatedAt' | 'authorId' | 'metrics'>): Promise<ApiResponse<ContentPiece>> {
    return contentApi.post('/content', data);
  }

  async updateContent(id: string, data: Partial<ContentPiece>): Promise<ApiResponse<ContentPiece>> {
    return contentApi.patch(`/content/${id}`, data);
  }

  async deleteContent(id: string): Promise<ApiResponse<void>> {
    return contentApi.delete(`/content/${id}`);
  }

  async duplicateContent(id: string): Promise<ApiResponse<ContentPiece>> {
    return contentApi.post(`/content/${id}/duplicate`);
  }

  // AI Content Generation
  async generateContent(request: ContentGenRequest): Promise<ApiResponse<ContentGenResponse>> {
    return contentApi.post('/generate', request);
  }

  async improveContent(contentId: string, instructions: string): Promise<ApiResponse<ContentGenResponse>> {
    return contentApi.post(`/content/${contentId}/improve`, { instructions });
  }

  async expandContent(contentId: string, targetLength: number): Promise<ApiResponse<ContentGenResponse>> {
    return contentApi.post(`/content/${contentId}/expand`, { targetLength });
  }

  async summarizeContent(contentId: string, maxLength: number): Promise<ApiResponse<ContentGenResponse>> {
    return contentApi.post(`/content/${contentId}/summarize`, { maxLength });
  }

  async translateContent(contentId: string, targetLanguage: string): Promise<ApiResponse<ContentGenResponse>> {
    return contentApi.post(`/content/${contentId}/translate`, { targetLanguage });
  }

  async adaptForPlatform(contentId: string, platform: SocialPlatform): Promise<ApiResponse<ContentGenResponse>> {
    return contentApi.post(`/content/${contentId}/adapt`, { platform });
  }

  // Brand Voice Management
  async getBrandVoices(): Promise<ApiResponse<BrandVoice[]>> {
    return contentApi.get('/brand-voices');
  }

  async getBrandVoice(id: string): Promise<ApiResponse<BrandVoice>> {
    return contentApi.get(`/brand-voices/${id}`);
  }

  async createBrandVoice(data: Omit<BrandVoice, 'id'>): Promise<ApiResponse<BrandVoice>> {
    return contentApi.post('/brand-voices', data);
  }

  async updateBrandVoice(id: string, data: Partial<BrandVoice>): Promise<ApiResponse<BrandVoice>> {
    return contentApi.patch(`/brand-voices/${id}`, data);
  }

  async deleteBrandVoice(id: string): Promise<ApiResponse<void>> {
    return contentApi.delete(`/brand-voices/${id}`);
  }

  async setDefaultBrandVoice(id: string): Promise<ApiResponse<void>> {
    return contentApi.post(`/brand-voices/${id}/set-default`);
  }

  // Content Calendar
  async getCalendars(): Promise<ApiResponse<ContentCalendar[]>> {
    return contentApi.get('/calendars');
  }

  async getCalendar(id: string): Promise<ApiResponse<ContentCalendar>> {
    return contentApi.get(`/calendars/${id}`);
  }

  async createCalendar(data: Omit<ContentCalendar, 'id' | 'entries'>): Promise<ApiResponse<ContentCalendar>> {
    return contentApi.post('/calendars', data);
  }

  async updateCalendar(id: string, data: Partial<ContentCalendar>): Promise<ApiResponse<ContentCalendar>> {
    return contentApi.patch(`/calendars/${id}`, data);
  }

  async deleteCalendar(id: string): Promise<ApiResponse<void>> {
    return contentApi.delete(`/calendars/${id}`);
  }

  async scheduleContent(data: {
    contentId: string;
    calendarId: string;
    scheduledDate: string;
    platforms: SocialPlatform[];
  }): Promise<ApiResponse<void>> {
    return contentApi.post('/calendars/schedule', data);
  }

  async unscheduleContent(contentId: string): Promise<ApiResponse<void>> {
    return contentApi.post(`/content/${contentId}/unschedule`);
  }

  async rescheduleContent(contentId: string, newDate: string): Promise<ApiResponse<void>> {
    return contentApi.patch(`/content/${contentId}/reschedule`, { scheduledDate: newDate });
  }

  // Publishing
  async publishContent(contentId: string, platforms: SocialPlatform[]): Promise<ApiResponse<{
    results: Array<{
      platform: SocialPlatform;
      success: boolean;
      postId?: string;
      error?: string;
    }>;
  }>> {
    return contentApi.post(`/content/${contentId}/publish`, { platforms });
  }

  async getPublishingStatus(contentId: string): Promise<ApiResponse<{
    status: 'pending' | 'publishing' | 'published' | 'failed';
    platforms: Array<{
      platform: SocialPlatform;
      status: 'pending' | 'publishing' | 'published' | 'failed';
      postId?: string;
      publishedAt?: string;
      error?: string;
    }>;
  }>> {
    return contentApi.get(`/content/${contentId}/publish-status`);
  }

  // Content Templates
  async getTemplates(params?: {
    type?: string;
    category?: string;
    tags?: string[];
  }): Promise<ApiResponse<Array<{
    id: string;
    name: string;
    description: string;
    type: string;
    category: string;
    template: string;
    variables: Array<{
      name: string;
      type: 'text' | 'number' | 'date' | 'select';
      required: boolean;
      options?: string[];
    }>;
    tags: string[];
  }>>> {
    return contentApi.get('/templates', { params });
  }

  async createFromTemplate(templateId: string, variables: Record<string, any>): Promise<ApiResponse<ContentPiece>> {
    return contentApi.post(`/templates/${templateId}/create`, { variables });
  }

  // Analytics & Performance
  async getContentMetrics(contentId: string): Promise<ApiResponse<{
    views: number;
    clicks: number;
    shares: number;
    likes: number;
    comments: number;
    conversions: number;
    engagementRate: number;
    platformBreakdown: Array<{
      platform: SocialPlatform;
      views: number;
      clicks: number;
      shares: number;
      likes: number;
      comments: number;
      engagementRate: number;
    }>;
  }>> {
    return contentApi.get(`/content/${contentId}/metrics`);
  }

  async getPerformanceAnalytics(params?: {
    timeRange?: '24h' | '7d' | '30d' | '90d';
    contentType?: string;
    platforms?: SocialPlatform[];
    brandVoice?: string;
  }): Promise<ApiResponse<{
    totalViews: number;
    totalEngagement: number;
    averageEngagementRate: number;
    bestPerformingContent: Array<{
      contentId: string;
      title: string;
      type: string;
      engagementRate: number;
      views: number;
    }>;
    platformPerformance: Array<{
      platform: SocialPlatform;
      posts: number;
      avgEngagementRate: number;
      totalViews: number;
    }>;
    contentTypePerformance: Array<{
      type: string;
      posts: number;
      avgEngagementRate: number;
      totalViews: number;
    }>;
    trends: Array<{
      date: string;
      views: number;
      engagement: number;
      posts: number;
    }>;
  }>> {
    return contentApi.get('/analytics/performance', { params });
  }

  // A/B Testing
  async createABTest(data: {
    name: string;
    contentIds: string[];
    trafficSplit: number[];
    duration: number; // in hours
    successMetric: 'views' | 'clicks' | 'shares' | 'conversions';
  }): Promise<ApiResponse<{
    id: string;
    name: string;
    status: 'draft' | 'running' | 'completed';
    startDate: string;
    endDate: string;
    variants: Array<{
      contentId: string;
      trafficPercentage: number;
    }>;
  }>> {
    return contentApi.post('/ab-tests', data);
  }

  async getABTestResults(testId: string): Promise<ApiResponse<{
    id: string;
    name: string;
    status: 'draft' | 'running' | 'completed';
    results: Array<{
      contentId: string;
      title: string;
      views: number;
      clicks: number;
      conversions: number;
      conversionRate: number;
      confidence: number;
      isWinner: boolean;
    }>;
    winner?: string;
    statisticalSignificance: boolean;
  }>> {
    return contentApi.get(`/ab-tests/${testId}/results`);
  }

  // Content Optimization
  async getSEOSuggestions(contentId: string): Promise<ApiResponse<{
    score: number;
    suggestions: Array<{
      type: 'title' | 'meta_description' | 'headings' | 'keywords' | 'readability';
      message: string;
      impact: 'low' | 'medium' | 'high';
      suggestion: string;
    }>;
    keywords: Array<{
      keyword: string;
      density: number;
      recommended: boolean;
    }>;
  }>> {
    return contentApi.get(`/content/${contentId}/seo-analysis`);
  }

  async getReadabilityAnalysis(contentId: string): Promise<ApiResponse<{
    fleschKincaidGrade: number;
    fleschReadingEase: number;
    sentences: number;
    words: number;
    avgWordsPerSentence: number;
    suggestions: Array<{
      type: 'sentence_length' | 'word_choice' | 'paragraph_length';
      message: string;
      suggestion: string;
    }>;
  }>> {
    return contentApi.get(`/content/${contentId}/readability`);
  }
}

export const contentService = new ContentService();