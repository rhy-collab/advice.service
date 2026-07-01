import { expect, test } from "@playwright/test";

test("client portal can create a demo matter and keep delivery pending", async ({ page }) => {
  await page.goto("/portal");

  await expect(page.getByRole("heading", { name: "Matters dashboard" })).toBeVisible();
  await page.getByLabel("Upload contract").getByLabel("Choose .docx file").setInputFiles({
    name: "playwright-demo-contract.docx",
    mimeType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    buffer: Buffer.from("demo docx bytes"),
  });
  await page.getByRole("button", { name: "Create matter" }).click();

  await expect(page.getByText("Matter created for playwright-demo-contract.docx")).toBeVisible();
  await expect(page.getByLabel("Client matters").getByText("playwright-demo-contract.docx")).toBeVisible();
  await expect(page.getByRole("button", { name: "Pending approval" }).first()).toBeDisabled();
});
