import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  // Global setup that runs once before all tests
  
  // Start a browser instance
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Wait for the app to be ready
    console.log('🚀 Setting up E2E tests...');
    await page.goto(config.projects[0].use.baseURL || 'http://localhost:3000');
    await page.waitForLoadState('networkidle');
    console.log('✅ Frontend is ready for testing');
    
    // You can add any global setup here, such as:
    // - Seeding test database
    // - Creating test users
    // - Setting up mock services
    // - Authentication setup
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
  
  console.log('✅ Global setup completed');
}

export default globalSetup;