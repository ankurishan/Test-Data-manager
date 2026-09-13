const {test,expect} = require('@playwright/test');
test ('First test',async ({page})=>
{

//const context = await browser.newContext();
//const page = await context.newPage
await page.goto("https://www.rahulshettyacademy.com/loginpagePractise/");
console.log(await page.title());
await expect(page).toHaveTitle('LoginPage Practise | Rahul Shetty Academy');
await page.locator("#username").fill("rahulshetty");
await page.locator("[name='password']").fill("password");
await page.locator("input#signInBtn").click();
await page.locator("#terms").check();
await expect(page.locator("#terms")).toBeChecked();
console.log(await page.locator("[style*='block']").textContent());
await expect(page.locator("[style*='block']")).toContainText('Incorrect username/password.');

});
