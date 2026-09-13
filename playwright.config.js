// @ts-check
import { defineConfig, devices } from '@playwright/test';

/**
 * @see https://playwright.dev/docs/test-configuration
 */
const config =({
 
  
  testDir: './tests',
  timeout: 40 * 1000,
  expect:{
    timeout: 40 * 1000
  },
  reporter:'html',
  use: {
    browserName:'webkit',
    trace: 'on-first-retry',
    headless:true
  },
});
module.exports=config;

