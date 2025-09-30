import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, AuthTokens } from '@/lib/api/types';
import { gatewayService } from '@/lib/api/services/gateway';
import { tokenManager } from '@/lib/api/client';

interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string, firstName: string, lastName: string) => Promise<boolean>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<boolean>;
  updateUser: (user: Partial<User>) => void;
  clearError: () => void;
  initializeAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await gatewayService.login({ email, password });
          
          if (response.success && response.data) {
            const { user, tokens } = response.data;
            
            // Store tokens in token manager
            tokenManager.setTokens(tokens.accessToken, tokens.refreshToken);
            
            set({
              user,
              tokens,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
            
            return true;
          } else {
            set({
              isLoading: false,
              error: response.error?.message || 'Login failed',
            });
            return false;
          }
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'Login failed',
          });
          return false;
        }
      },

      register: async (email: string, password: string, firstName: string, lastName: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await gatewayService.register({
            email,
            password,
            firstName,
            lastName,
          });
          
          if (response.success && response.data) {
            const { user, tokens } = response.data;
            
            // Store tokens in token manager
            tokenManager.setTokens(tokens.accessToken, tokens.refreshToken);
            
            set({
              user,
              tokens,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
            
            return true;
          } else {
            set({
              isLoading: false,
              error: response.error?.message || 'Registration failed',
            });
            return false;
          }
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'Registration failed',
          });
          return false;
        }
      },

      logout: async () => {
        set({ isLoading: true });
        
        try {
          // Call logout endpoint to invalidate server-side session
          await gatewayService.logout();
        } catch (error) {
          // Continue with local logout even if server call fails
          console.error('Logout server call failed:', error);
        } finally {
          // Clear local storage and state
          tokenManager.clearTokens();
          set({
            user: null,
            tokens: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      refreshToken: async () => {
        const { tokens } = get();
        
        if (!tokens?.refreshToken) {
          return false;
        }
        
        try {
          const response = await gatewayService.refreshToken({
            refreshToken: tokens.refreshToken,
          });
          
          if (response.success && response.data) {
            const newTokens = response.data;
            
            // Store new tokens
            tokenManager.setTokens(newTokens.accessToken, newTokens.refreshToken);
            
            set({
              tokens: newTokens,
              error: null,
            });
            
            return true;
          } else {
            // Refresh failed, logout user
            get().logout();
            return false;
          }
        } catch (error) {
          // Refresh failed, logout user
          get().logout();
          return false;
        }
      },

      updateUser: (userUpdate: Partial<User>) => {
        const { user } = get();
        if (user) {
          set({
            user: { ...user, ...userUpdate },
          });
        }
      },

      clearError: () => {
        set({ error: null });
      },

      initializeAuth: async () => {
        // Check if user is already logged in (has tokens)
        if (tokenManager.isAuthenticated()) {
          set({ isLoading: true });
          
          try {
            // Verify the token and get user info
            const response = await gatewayService.getCurrentUser();
            
            if (response.success && response.data) {
              const user = response.data;
              const accessToken = tokenManager.getAccessToken();
              const refreshToken = tokenManager.getRefreshToken();
              
              if (accessToken && refreshToken) {
                set({
                  user,
                  tokens: {
                    accessToken,
                    refreshToken,
                    expiresAt: Date.now() + 15 * 60 * 1000, // Assume 15 min expiry
                  },
                  isAuthenticated: true,
                  isLoading: false,
                  error: null,
                });
                return;
              }
            }
            
            // Token invalid, clear everything
            tokenManager.clearTokens();
            set({
              user: null,
              tokens: null,
              isAuthenticated: false,
              isLoading: false,
              error: null,
            });
          } catch (error) {
            // Token verification failed, clear everything
            tokenManager.clearTokens();
            set({
              user: null,
              tokens: null,
              isAuthenticated: false,
              isLoading: false,
              error: null,
            });
          }
        } else {
          set({
            isLoading: false,
          });
        }
      },
    }),
    {
      name: 'plasma-auth-storage',
      partialize: (state) => ({
        // Only persist user info, tokens are handled by tokenManager
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Auto-initialize auth on store creation
if (typeof window !== 'undefined') {
  useAuthStore.getState().initializeAuth();
}