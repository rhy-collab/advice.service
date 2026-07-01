import { expect, test } from "@playwright/test";

test("attorney workbench can action prep, record minutes, and approve", async ({ page }) => {
  await page.goto("/attorney");

  await expect(page.getByRole("heading", { name: "Review AI prep and approve delivery" })).toBeVisible();
  await expect(page.getByRole("button", { name: /vendor-saas-agreement/ })).toBeVisible();

  await page.getByTitle("Apply issue").first().click();
  await expect(page.getByText(/marked as apply/)).toBeVisible();

  await page.getByLabel("Review minutes").fill("18");
  await page.getByRole("button", { name: "Save" }).click();
  await expect(page.getByText("Review minutes saved.")).toBeVisible();

  await page.getByRole("button", { name: "Approve" }).click();
  await expect(page.getByText("Matter approved for client delivery.")).toBeVisible();
});
