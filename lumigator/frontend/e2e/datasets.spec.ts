import { test, expect } from '@playwright/test';
import path from 'path'
import fs from 'fs'

// get the sample dataset absolute file path
const currentDir = path.dirname(new URL(import.meta.url).pathname);
const sampleDatasetFilePath = path.resolve(currentDir, '../../sample_data/dialogsum_exc.csv');

test('successfully uploads a dataset', async ({ page }) => {
  await page.goto('/');

  const fileChooserPromise = page.waitForEvent('filechooser');
  // find & click the provide dataset button
  const button = await page.getByRole('button', { name: 'Provide Dataset' });
  await button.click();

  const fileChooser = await fileChooserPromise;

  // validate that the sample dataset file exists in the expected directory
  console.log('Resolved File Path:', sampleDatasetFilePath);
  if (!fs.existsSync(sampleDatasetFilePath)) {
    console.log('Error: File does not exist at', sampleDatasetFilePath);
    return;
  }

  // choose the sample dataset file from the file chooser dialog
  await fileChooser.setFiles(sampleDatasetFilePath);

  // click the upload button from the confirmation modal
  const uploadButton = await page.getByRole('button', { name: 'Upload' });
  await uploadButton.click();

  // wait for the api requests to upload the file and refetch the datasets to finish
  const [response] = await Promise.all([
    page.waitForResponse(response => response.url().includes('datasets') && response.status() === 201 && response.request().method() === 'POST'),
  page.waitForRequest(request => request.url().includes('datasets') && request.method() === 'GET')
]);

 // get the returned filename and id from the api response
  const { id, filename } = await response.json();

  // wait for the new table row with the dataset id and filename to be rendered, (ids are shortened so we only check the first 20 characters)
  await expect(page.locator(`table tr:has(td:text("${id.slice(0, 20)}")):has(td:text("${filename}"))`)).toBeVisible();
})
