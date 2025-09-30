import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    // Clear any existing auth state
    await page.context().clearCookies();
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });

  test('should redirect to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Should redirect to login page
    await expect(page).toHaveURL(/.*\/auth\/login/);
    
    // Check login form elements
    await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/password/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });

  test('should show validation errors for invalid login', async ({ page }) => {
    await page.goto('/auth/login');
    
    // Try to submit form without filling fields
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Check for validation errors
    await expect(page.getByText(/email is required/i)).toBeVisible();
    await expect(page.getByText(/password is required/i)).toBeVisible();
  });

  test('should handle login with invalid credentials', async ({ page }) => {
    await page.goto('/auth/login');
    
    // Fill form with invalid credentials
    await page.getByLabel(/email/i).fill('test@example.com');
    await page.getByLabel(/password/i).fill('wrongpassword');
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Check for error message
    await expect(page.getByText(/invalid credentials/i)).toBeVisible();
    
    // Should still be on login page
    await expect(page).toHaveURL(/.*\/auth\/login/);
  });

  test('should successfully login with valid credentials', async ({ page }) => {
    // Mock successful login response
    await page.route('**/api/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            user: {
              id: '1',
              email: 'test@example.com',
              firstName: 'Test',
              lastName: 'User',
              role: 'admin',
            },
            token: 'mock-jwt-token',
          },
        }),
      });
    });
    
    await page.goto('/auth/login');
    
    // Fill form with valid credentials
    await page.getByLabel(/email/i).fill('test@example.com');
    await page.getByLabel(/password/i).fill('password');
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*\/dashboard/);
    
    // Check dashboard elements
    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
    await expect(page.getByText(/welcome back/i)).toBeVisible();
  });

  test('should show registration form', async ({ page }) => {
    await page.goto('/auth/login');
    
    // Click register link
    await page.getByRole('link', { name: /create account/i }).click();
    
    // Should navigate to register page
    await expect(page).toHaveURL(/.*\/auth\/register/);
    
    // Check registration form elements
    await expect(page.getByRole('heading', { name: /create account/i })).toBeVisible();
    await expect(page.getByLabel(/first name/i)).toBeVisible();
    await expect(page.getByLabel(/last name/i)).toBeVisible();
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/password/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /create account/i })).toBeVisible();
  });

  test('should successfully register new user', async ({ page }) => {
    // Mock successful registration response
    await page.route('**/api/auth/register', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            user: {
              id: '2',
              email: 'newuser@example.com',
              firstName: 'New',
              lastName: 'User',
              role: 'user',
            },
            token: 'mock-jwt-token-2',
          },
        }),
      });
    });
    
    await page.goto('/auth/register');
    
    // Fill registration form
    await page.getByLabel(/first name/i).fill('New');
    await page.getByLabel(/last name/i).fill('User');
    await page.getByLabel(/email/i).fill('newuser@example.com');
    await page.getByLabel(/password/i).fill('password123');
    await page.getByRole('button', { name: /create account/i }).click();
    
    // Should redirect to dashboard after successful registration
    await expect(page).toHaveURL(/.*\/dashboard/);
    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
  });

  test('should logout user', async ({ page }) => {
    // Mock login first
    await page.route('**/api/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            user: {
              id: '1',
              email: 'test@example.com',
              firstName: 'Test',
              lastName: 'User',
              role: 'admin',
            },
            token: 'mock-jwt-token',
          },
        }),
      });
    });
    
    // Mock logout
    await page.route('**/api/auth/logout', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      });
    });
    
    // Login first
    await page.goto('/auth/login');
    await page.getByLabel(/email/i).fill('test@example.com');
    await page.getByLabel(/password/i).fill('password');
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Wait for dashboard to load
    await expect(page).toHaveURL(/.*\/dashboard/);
    
    // Click user menu
    await page.getByRole('button').filter({ hasText: /test user/i }).click();
    
    // Click logout
    await page.getByRole('menuitem', { name: /logout/i }).click();
    
    // Should redirect to login page
    await expect(page).toHaveURL(/.*\/auth\/login/);
    await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
  });

  test('should persist authentication across page refreshes', async ({ page }) => {
    // Mock login
    await page.route('**/api/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            user: {
              id: '1',
              email: 'test@example.com',
              firstName: 'Test',
              lastName: 'User',
              role: 'admin',
            },
            token: 'mock-jwt-token',
          },
        }),
      });
    });
    
    // Login
    await page.goto('/auth/login');
    await page.getByLabel(/email/i).fill('test@example.com');
    await page.getByLabel(/password/i).fill('password');
    await page.getByRole('button', { name: /sign in/i }).click();
    
    await expect(page).toHaveURL(/.*\/dashboard/);
    
    // Refresh the page
    await page.reload();
    
    // Should still be authenticated and on dashboard
    await expect(page).toHaveURL(/.*\/dashboard/);
    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
  });
});