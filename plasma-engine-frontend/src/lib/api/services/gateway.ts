import { gatewayApi } from '../client';
import { 
  User, 
  AuthTokens, 
  LoginRequest, 
  RegisterRequest, 
  RefreshTokenRequest,
  ApiResponse,
  SystemHealth,
  ServiceStatus
} from '../types';

export class GatewayService {
  // Authentication
  async login(data: LoginRequest): Promise<ApiResponse<{ user: User; tokens: AuthTokens }>> {
    return gatewayApi.post('/auth/login', data);
  }

  async register(data: RegisterRequest): Promise<ApiResponse<{ user: User; tokens: AuthTokens }>> {
    return gatewayApi.post('/auth/register', data);
  }

  async refreshToken(data: RefreshTokenRequest): Promise<ApiResponse<AuthTokens>> {
    return gatewayApi.post('/auth/refresh', data);
  }

  async logout(): Promise<ApiResponse<void>> {
    return gatewayApi.post('/auth/logout');
  }

  async verifyToken(): Promise<ApiResponse<User>> {
    return gatewayApi.get('/auth/verify');
  }

  // User Management
  async getCurrentUser(): Promise<ApiResponse<User>> {
    return gatewayApi.get('/users/me');
  }

  async updateProfile(data: Partial<User>): Promise<ApiResponse<User>> {
    return gatewayApi.patch('/users/me', data);
  }

  async changePassword(data: { 
    currentPassword: string; 
    newPassword: string; 
  }): Promise<ApiResponse<void>> {
    return gatewayApi.post('/users/me/change-password', data);
  }

  async uploadAvatar(file: File): Promise<ApiResponse<{ avatarUrl: string }>> {
    return gatewayApi.upload('/users/me/avatar', file);
  }

  // Organization Management (Admin only)
  async getOrganizationUsers(): Promise<ApiResponse<User[]>> {
    return gatewayApi.get('/users');
  }

  async inviteUser(data: { 
    email: string; 
    role: string; 
    firstName?: string; 
    lastName?: string; 
  }): Promise<ApiResponse<void>> {
    return gatewayApi.post('/users/invite', data);
  }

  async updateUserRole(userId: string, role: string): Promise<ApiResponse<void>> {
    return gatewayApi.patch(`/users/${userId}/role`, { role });
  }

  async deactivateUser(userId: string): Promise<ApiResponse<void>> {
    return gatewayApi.delete(`/users/${userId}`);
  }

  // API Key Management
  async getApiKeys(): Promise<ApiResponse<Array<{
    id: string;
    name: string;
    lastUsed?: string;
    createdAt: string;
    permissions: string[];
  }>>> {
    return gatewayApi.get('/api-keys');
  }

  async createApiKey(data: {
    name: string;
    permissions: string[];
    expiresAt?: string;
  }): Promise<ApiResponse<{
    id: string;
    key: string;
    name: string;
    permissions: string[];
  }>> {
    return gatewayApi.post('/api-keys', data);
  }

  async revokeApiKey(keyId: string): Promise<ApiResponse<void>> {
    return gatewayApi.delete(`/api-keys/${keyId}`);
  }

  // System Health & Monitoring
  async getSystemHealth(): Promise<ApiResponse<SystemHealth>> {
    return gatewayApi.get('/health/system');
  }

  async getServiceStatuses(): Promise<ApiResponse<ServiceStatus[]>> {
    return gatewayApi.get('/health/services');
  }

  async getUsageStats(): Promise<ApiResponse<{
    totalRequests: number;
    totalUsers: number;
    activeUsers: number;
    requestsToday: number;
    averageResponseTime: number;
    errorRate: number;
  }>> {
    return gatewayApi.get('/admin/usage-stats');
  }

  async getAuditLogs(params?: {
    userId?: string;
    action?: string;
    startDate?: string;
    endDate?: string;
    page?: number;
    limit?: number;
  }): Promise<ApiResponse<Array<{
    id: string;
    userId: string;
    action: string;
    resource: string;
    details: Record<string, any>;
    ipAddress: string;
    userAgent: string;
    timestamp: string;
  }>>> {
    return gatewayApi.get('/admin/audit-logs', { params });
  }

  // Rate Limiting & Quotas
  async getUserQuotas(): Promise<ApiResponse<{
    requests: { used: number; limit: number; resetAt: string };
    uploads: { used: number; limit: number; resetAt: string };
    storage: { used: number; limit: number };
  }>> {
    return gatewayApi.get('/users/me/quotas');
  }

  // Webhook Management
  async getWebhooks(): Promise<ApiResponse<Array<{
    id: string;
    name: string;
    url: string;
    events: string[];
    isActive: boolean;
    createdAt: string;
    lastDelivery?: string;
  }>>> {
    return gatewayApi.get('/webhooks');
  }

  async createWebhook(data: {
    name: string;
    url: string;
    events: string[];
    secret?: string;
  }): Promise<ApiResponse<{
    id: string;
    name: string;
    url: string;
    events: string[];
    secret: string;
  }>> {
    return gatewayApi.post('/webhooks', data);
  }

  async updateWebhook(id: string, data: {
    name?: string;
    url?: string;
    events?: string[];
    isActive?: boolean;
  }): Promise<ApiResponse<void>> {
    return gatewayApi.patch(`/webhooks/${id}`, data);
  }

  async deleteWebhook(id: string): Promise<ApiResponse<void>> {
    return gatewayApi.delete(`/webhooks/${id}`);
  }

  async testWebhook(id: string): Promise<ApiResponse<{
    success: boolean;
    responseTime: number;
    statusCode: number;
    error?: string;
  }>> {
    return gatewayApi.post(`/webhooks/${id}/test`);
  }

  // GraphQL Federation
  async getGraphQLSchema(): Promise<ApiResponse<{ schema: string }>> {
    return gatewayApi.get('/graphql/schema');
  }

  async getSubgraphStatuses(): Promise<ApiResponse<Array<{
    name: string;
    url: string;
    status: 'healthy' | 'unhealthy' | 'degraded';
    lastCheck: string;
  }>>> {
    return gatewayApi.get('/graphql/subgraphs/status');
  }
}

export const gatewayService = new GatewayService();