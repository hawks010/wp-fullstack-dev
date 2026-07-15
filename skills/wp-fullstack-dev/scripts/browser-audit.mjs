#!/usr/bin/env node
/**
 * Browser runtime audit: load pages and report console errors, page exceptions,
 * failed requests, and HTTP error responses. Evidence for JS/React/CSS debugging.
 *
 * Usage: node browser-audit.mjs <url> [more urls...]
 * Requires Playwright in the target project (npm i -D playwright) or globally.
 *
 * @author Sonny x Inkfire
 */

const urls = process.argv.slice(2);
if (urls.length === 0) {
  console.error('Usage: node browser-audit.mjs <url> [more urls...]');
  process.exit(2);
}

let chromium;
try {
  ({ chromium } = await import('playwright'));
} catch {
  try {
    ({ chromium } = await import('@playwright/test'));
  } catch {
    console.error('Playwright is not installed. Run: npm i -D playwright');
    process.exit(2);
  }
}

const browser = await chromium.launch({ headless: true });
let failures = 0;

for (const url of urls) {
  const findings = [];
  const page = await browser.newPage();
  page.on('console', (message) => {
    if (message.type() === 'error' || message.type() === 'warning') {
      findings.push(`console.${message.type()}: ${message.text()}`);
    }
  });
  page.on('pageerror', (error) => findings.push(`pageerror: ${error.message}`));
  page.on('requestfailed', (request) => {
    findings.push(`requestfailed: ${request.method()} ${request.url()} — ${request.failure()?.errorText}`);
  });
  page.on('response', (response) => {
    if (response.status() >= 400) {
      findings.push(`http ${response.status()}: ${response.url()}`);
    }
  });

  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
  } catch (error) {
    findings.push(`navigation: ${error.message}`);
  }
  await page.close();

  if (findings.length === 0) {
    console.log(`PASS ${url}`);
  } else {
    failures += 1;
    console.log(`FAIL ${url}`);
    for (const finding of findings) {
      console.log(`  ${finding}`);
    }
  }
}

await browser.close();
process.exit(failures > 0 ? 1 : 0);
