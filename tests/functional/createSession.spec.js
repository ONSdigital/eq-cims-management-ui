import { test, expect } from "@playwright/test";

test("renders initial index page with expected contents", async ({ page }) => {
  await page.goto("http://localhost:5100/");

  await expect(page).toHaveTitle("Collection Instrument Migration Service (CIMS)");
});

test("displays confirmation text when session is successfully created", async ({ page }) => {
  await page.goto("http://localhost:5100/");

  const createSessionButton = page.getByTestId("create-session-btn");

  createSessionButton.click();

  await expect(page.getByText("Session created")).toBeVisible();
});
