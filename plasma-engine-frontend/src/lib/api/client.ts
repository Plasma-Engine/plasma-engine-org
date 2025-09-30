import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import { ApiResponse, ApiError } from './types';

// Environment configuration
const API_CONFIG = {
  gateway: process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:8000',
  research: process.env.NEXT_PUBLIC_RESEARCH_URL || 'http://localhost:8001',
  brand: process.env.NEXT_PUBLIC_BRAND_URL || 'http://localhost:8002',
  content: process.env.NEXT_PUBLIC_CONTENT_URL || 'http://localhost:8003',
  agent: process.env.NEXT_PUBLIC_AGENT_URL || 'http://localhost:8004',
};

// Token management
class TokenManager {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor() {
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('accessToken');
      this.refreshToken = localStorage.getItem('refreshToken');
    }
  }

  setTokens(accessToken: string, refreshToken: string): void {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
    
    if (typeof window !== 'undefined') {
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
    }
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }

  getRefreshToken(): string | null {
    return this.refreshToken;
  }

  clearTokens(): void {
    this.accessToken = null;
    this.refreshToken = null;
    
    if (typeof window !== 'undefined') {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    }
  }

  isAuthenticated(): boolean {
    return !!this.accessToken;
  }
}

export const tokenManager = new TokenManager();

// Base API client
class ApiClient {
  private client: AxiosInstance;
  private serviceName: string;

  constructor(serviceName: keyof typeof API_CONFIG) {
    this.serviceName = serviceName;
    this.client = axios.create({
      baseURL: API_CONFIG[serviceName],
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = tokenManager.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling and token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

        // Handle 401 Unauthorized
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = tokenManager.getRefreshToken();
            if (!refreshToken) {
              throw new Error('No refresh token available');
            }

            // Attempt to refresh token
            const response = await axios.post(`${API_CONFIG.gateway}/auth/refresh`, {
              refreshToken,
            });

            const { accessToken, refreshToken: newRefreshToken } = response.data.data;
            tokenManager.setTokens(accessToken, newRefreshToken);

            // Retry original request
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${accessToken}`;
            }
            return this.client(originalRequest);
          } catch (refreshError) {
            // Refresh failed, clear tokens and redirect to login
            tokenManager.clearTokens();
            if (typeof window !== 'undefined') {
              window.location.href = '/auth/login';
            }
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(this.handleApiError(error));
      }
    );
  }

  private handleApiError(error: AxiosError): ApiError {
    if (error.response?.data) {
      const apiError = error.response.data as any;
      return {
        code: apiError.code || 'API_ERROR',
        message: apiError.message || 'An error occurred',
        details: apiError.details || {},
      };
    }

    if (error.request) {
      return {
        code: 'NETWORK_ERROR',
        message: 'Network error occurred. Please check your connection.',
        details: {},
      };
    }

    return {
      code: 'UNKNOWN_ERROR',
      message: error.message || 'An unknown error occurred',
      details: {},
    };
  }

  // Generic request methods
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.get(url, config);
      return response.data;
    } catch (error) {
      return {
        success: false,
        error: error as ApiError,
      };
    }
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.post(url, data, config);
      return response.data;
    } catch (error) {
      return {
        success: false,
        error: error as ApiError,
      };
    }
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.put(url, data, config);
      return response.data;
    } catch (error) {
      return {
        success: false,
        error: error as ApiError,
      };
    }
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.patch(url, data, config);
      return response.data;
    } catch (error) {
      return {
        success: false,
        error: error as ApiError,
      };
    }
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.delete(url, config);
      return response.data;
    } catch (error) {
      return {
        success: false,
        error: error as ApiError,
      };
    }
  }

  // File upload method
  async upload<T = any>(url: string, file: File, onProgress?: (progress: number) => void): Promise<ApiResponse<T>> {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await this.client.post(url, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(progress);
          }
        },
      });
      return response.data;
    } catch (error) {
      return {
        success: false,
        error: error as ApiError,
      };
    }
  }
}

// Service-specific clients
export const gatewayApi = new ApiClient('gateway');
export const researchApi = new ApiClient('research');
export const brandApi = new ApiClient('brand');
export const contentApi = new ApiClient('content');
export const agentApi = new ApiClient('agent');

// Health check utility
export const checkServiceHealth = async (): Promise<Record<string, boolean>> => {
  const services = ['gateway', 'research', 'brand', 'content', 'agent'] as const;
  const healthStatus: Record<string, boolean> = {};

  await Promise.allSettled(
    services.map(async (service) => {
      try {
        const client = new ApiClient(service);
        const response = await client.get('/health');
        healthStatus[service] = response.success;
      } catch {
        healthStatus[service] = false;
      }
    })
  );

  return healthStatus;
};

// WebSocket connection utility
export class WebSocketManager {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  constructor(private url: string) {}

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const token = tokenManager.getAccessToken();
        const wsUrl = `${this.url}?token=${token}`;
        
        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.socket.onclose = () => {
          console.log('WebSocket disconnected');
          this.handleReconnect();
        };

        this.socket.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect();
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }

  send(data: any): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    }
  }

  onMessage(callback: (data: any) => void): void {
    if (this.socket) {
      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          callback(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
    }
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

export default ApiClient;