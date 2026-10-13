import re

from playwright.sync_api import expect


def test_user_creates_car_in_browser(page, live_server):
    page.goto(f"{live_server}/cars/new")
    page.get_by_label("Make", exact=True).fill("Toyota")
    page.get_by_label("Model", exact=True).fill("Yaris")
    page.get_by_label("Year", exact=True).fill("2020")
    page.get_by_label("Color", exact=False).fill("Blue")
    page.get_by_role("button", name="Create car").click()
    expect(page).to_have_url(re.compile(r"/cars/\d+$"))
    expect(page.get_by_role("heading", name="Toyota Yaris")).to_be_visible()


def test_user_edits_car_and_change_survives_reload(page, live_server):
    page.goto(f"{live_server}/cars/new")
    page.get_by_label("Make", exact=True).fill("Honda")
    page.get_by_label("Model", exact=True).fill("Civic")
    page.get_by_label("Year", exact=True).fill("2022")
    page.get_by_label("Color", exact=False).fill("Blue")
    page.get_by_role("button", name="Create car").click()
    expect(page).to_have_url(re.compile(r"/cars/\d+$"))

    page.get_by_role("link", name="Edit car").click()
    # 使用最精准的 input 标签 ID 定位，确保在 Linux 环境下不会匹配错
    model_input = page.locator("input#car-model")
    year_input = page.locator("input#car-year")
    
    model_input.fill("Accord")
    year_input.fill("2023")
    
    # 确认 Playwright 真的把值填进去了
    expect(model_input).to_have_value("Accord")
    
    page.get_by_role("button", name="Save changes").click()
    # 等待网络请求完成，防止 CI 环境因机器慢而提前刷新
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)
    
    # 强制刷新，确保从数据库中读取最新数据
    page.reload()
    expect(page.locator("#car-model")).to_have_text("Accord", timeout=15000)
    expect(page.locator("#car-year")).to_have_text("2023", timeout=15000)

    page.reload()
    expect(page.locator("#car-model")).to_have_text("Accord")
    expect(page.locator("#car-year")).to_have_text("2023")