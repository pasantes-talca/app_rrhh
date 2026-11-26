import { expect, test } from "@playwright/test";

test("abre el portal React", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Bienvenido" })).toBeVisible();
});
