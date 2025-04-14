import { test, expect } from '@playwright/test'
import { log } from 'console';
import path from 'path'

// get the sample dataset absolute file path
const currentDir = path.dirname(new URL(import.meta.url).pathname)
const sampleDatasetFilePath = path.resolve(
  currentDir,
  '../../sample_data/summarization/dialogsum_mini_no_gt.csv',
)
const submittedFileName = 'dialogsum_mini_no_gt.csv';
test('Launch a GT workflow', async ({ page }) => {
  await page.goto('/')

  // find & click the provide dataset button and capture the system file chooser dialog
  const fileChooserPromise = page.waitForEvent('filechooser')
  const button = page.getByRole('button', { name: 'Provide Dataset' })
  await button.click()
  const fileChooser = await fileChooserPromise

  // choose the sample dataset file from the file chooser dialog
  await fileChooser.setFiles(sampleDatasetFilePath)

  // click the upload button from the confirmation modal
  const uploadButton = page.getByRole('button', { name: 'Upload' })
  await uploadButton.click()

  // wait for the api requests to upload the file and refetch the datasets
  const [response] = await Promise.all([
    page.waitForResponse(
      (response) =>
        response.url().includes('datasets') &&
        response.status() === 201 &&
        response.request().method() === 'POST',
    ),
    page.waitForRequest(
      (request) => request.url().includes('datasets') && request.method() === 'GET',
    ),
  ])

  // get the returned filename and id from the api response
  const { id, filename } = await response.json()

  // wait for the new table row with the new dataset id and filename to be rendered, (ids are shortened so we only check the first 20 characters)
  await expect(
    page.locator(`table tr:has(td:text("${id.slice(0, 20)}")):has(td:text("${filename}"))`),
  ).toBeVisible()


  const datasetRow = page.locator('tr').filter({ hasText: 'dialogsum_mini_no_gt.csv' }).first();
  await expect(datasetRow).toBeVisible({ timeout: 5000 });
  await datasetRow.click();

  // Wait for the sidebar (assumed to have the class "sliding-panel") to appear.
  const sidebar = page.locator('.sliding-panel');
  await expect(sidebar).toBeVisible({ timeout: 5000 });

  // Within the sidebar, find and click the "Generate Ground Truth" button.
  const generateGtButton = sidebar.getByRole('button', { name: 'Generate Ground Truth' });
  await expect(generateGtButton).toBeVisible({ timeout: 5000 });
  await generateGtButton.click();

  // Now wait for the popup dialog to appear (assumed to be a role="dialog").
  const popupContainer = page.locator('.popup');
  await expect(popupContainer).toBeVisible({ timeout: 5000 });

  const [jobResponse] = await Promise.all([
    page.waitForResponse(
      (res) =>
        res.url().includes('/jobs') &&
        res.request().method() === 'POST' &&
        res.status() === 201
    ),
    // Click the "Start Generating" button.
    popupContainer.getByRole('button', { name: 'Start Generating' }).click(),
  ]);

  // (3) Extract the job ID from the API response.
  const jobData = await jobResponse.json();
  const jobId = jobData.id; // e.g., "712afa3f-ee81-41c0-8f1b-8939c2bf0ee4"

  // (4) Switch to the "Ground Truth Jobs" tab to see the job’s status.
  // Adjust the selector if your tab has a different structure.
  const groundTruthJobsTab = page.locator('button').filter({ hasText: 'Ground Truth Jobs' });
  await groundTruthJobsTab.click();

  // (5) Wait up to 10 minutes for the job to appear with status "succeeded".
  // The table row typically includes the job ID or name, plus a status cell that
  // shows "succeeded" with a .p-tag-success element or text. Here we use the ID:
  // Locate all table rows that display the submitted file name and have a succeeded indicator.
  const jobRows = page.locator(`tr:has(td:has-text("${submittedFileName}")):has(.p-tag-success)`);
  console.log('Job Rows: %o', jobRows);


  // Wait until the last row (i.e. the bottom occurrence) is visible (up to 10 minutes).
  await expect(jobRows.last()).toBeVisible({ timeout: 600000 });

  // Optionally, assert that the status text is "succeeded".
  await expect(jobRows.last().locator('.p-tag-label')).toHaveText(/succeeded/i);

})
