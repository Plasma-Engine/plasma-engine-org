async function globalTeardown() {
  // Global teardown that runs once after all tests
  
  console.log('🧹 Running global teardown...');
  
  try {
    // You can add any cleanup here, such as:
    // - Cleaning up test database
    // - Stopping mock services
    // - Cleaning up test files
    // - Resetting test environment
    
    console.log('✅ Global teardown completed');
  } catch (error) {
    console.error('❌ Global teardown failed:', error);
    throw error;
  }
}

export default globalTeardown;