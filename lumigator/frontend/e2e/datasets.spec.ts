import { test, expect } from '@playwright/test'
import { log } from 'console';
import path from 'path';
import fs from 'fs';

// get the sample dataset absolute file path
const currentDir = path.dirname(new URL(import.meta.url).pathname);
const sampleDatasetFilePath = path.resolve(
  currentDir,
  '../../sample_data/summarization/dialogsum_mini_no_gt.csv'
);

// Create a unique file name by appending a timestamp.
const timestamp = Date.now();
const dynamicFileName = `dialogsum_mini_no_gt_${timestamp}.csv`;
let submittedFileName = dynamicFileName;


test('Launch a GT workflow with unique file and fail early on job failure', async ({ page }) => {
  // Increase test timeout to 10 minutes.
  test.setTimeout(600000);
  await page.goto('/');

  // Trigger file chooser by clicking "Provide Dataset".
  const fileChooserPromise = page.waitForEvent('filechooser');
  const provideDatasetButton = page.getByRole('button', { name: 'Provide Dataset' });
  await provideDatasetButton.click();
  const fileChooser = await fileChooserPromise;

  const fileBuffer = fs.readFileSync(sampleDatasetFilePath);
  await fileChooser.setFiles({
    name: dynamicFileName,
    mimeType: 'text/csv',
    buffer: fileBuffer,
  });

  // Click the "Upload" button from the confirmation modal.
  const uploadButton = page.getByRole('button', { name: 'Upload' });
  await uploadButton.click();

  // Wait for the API requests for upload and refresh.
  const [response] = await Promise.all([
    page.waitForResponse(
      (response) =>
        response.url().includes('datasets') &&
        response.status() === 201 &&
        response.request().method() === 'POST'
    ),
    page.waitForRequest(
      (request) => request.url().includes('datasets') && request.method() === 'GET'
    ),
  ]);

  // Extract returned dataset id and filename from the API response.
  const { id, filename } = await response.json();

  // Wait for the new dataset row to appear in the table.
  await expect(
    page.locator(`table tr:has(td:text("${id.slice(0, 20)}")):has(td:text("${filename}"))`)
  ).toBeVisible();

  // Click the dataset row (using the unique submittedFileName).
  const datasetRow = page.locator('tr').filter({ hasText: submittedFileName }).first();
  await expect(datasetRow).toBeVisible({ timeout: 5000 });
  await datasetRow.click();

  // Wait for the sidebar (with class "sliding-panel") to appear.
  const sidebar = page.locator('.sliding-panel');
  await expect(sidebar).toBeVisible({ timeout: 5000 });

  // In the sidebar, click the "Generate Ground Truth" button.
  const generateGtButton = sidebar.getByRole('button', { name: 'Generate Ground Truth' });
  await expect(generateGtButton).toBeVisible({ timeout: 5000 });
  await generateGtButton.click();

  // Wait for the popup to appear (identified by its ".popup" class).
  const popupContainer = page.locator('.popup');
  await expect(popupContainer).toBeVisible({ timeout: 5000 });

  // Click "Start Generating" and wait for the API to create the job.
  const [jobResponse] = await Promise.all([
    page.waitForResponse(
      (res) =>
        res.url().includes('/jobs') &&
        res.request().method() === 'POST' &&
        res.status() === 201
    ),
    popupContainer.getByRole('button', { name: 'Start Generating' }).click(),
  ]);

  // Extract the job ID from the API response.
  const jobData = await jobResponse.json();
  const jobId = jobData.id; // e.g., "712afa3f-ee81-41c0-8f1b-8939c2bf0ee4"

  // Switch to the "Ground Truth Jobs" tab.
  const groundTruthJobsTab = page.locator('button').filter({ hasText: 'Ground Truth Jobs' });
  await groundTruthJobsTab.click();


  await page.waitForFunction(
    (fileName) => {
      const rows = Array.from(document.querySelectorAll('tr')).filter(row =>
        (row.textContent || "").includes(fileName)
      );
      if (rows.length === 0) return false;
      const lastRow = rows[rows.length - 1];
      const statusEl = lastRow.querySelector('.p-tag-label');
      if (!statusEl || !(statusEl instanceof HTMLElement)) return false;
      const status = statusEl.innerText.trim().toLowerCase();
      if (status === 'failed') {
          throw new Error('Job failed');
      }
      return status === 'succeeded';
    },
    submittedFileName,
    { timeout: 600000 }
  );

  // Assert that the last row’s status is "succeeded".
  const jobRows = page.locator(`tr:has(td:has-text("${submittedFileName}"))`);
  const lastJobRow = jobRows.last();
  await expect(lastJobRow.locator('.p-tag-label')).toHaveText(/succeeded/i);
});
