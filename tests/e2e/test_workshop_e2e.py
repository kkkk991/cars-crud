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
    page.get_by_label("Color", exact=False).fill("White")
    page.get_by_role("button", name="Create car").click()

    # page.get_by_role("link", name="Edit car").click()
    # page.get_by_label("Model", exact=True).fill("Accord")
    # page.get_by_label("Year", exact=True).fill("2023")
    # page.get_by_role("button", name="Save changes").click()

    # # expect(page.get_by_role("heading", name="Honda Accord")).to_be_visible(timeout=15000)
    # expect(page.locator("#car-model")).to_have_text("Accord")
    # expect(page.locator("#car-year")).to_have_text("2023")

    # page.reload()
    # expect(page.locator("#car-model")).to_have_text("Accord")
    # expect(page.locator("#car-year")).to_have_text("2023")

    page.get_by_role("link", name="Edit car").click()

    # 1. 关键修复：在修改之前，显式等待表单加载出旧数据 "Civic"
    # 确保页面从后端拉取到了旧数据，我们再动手修改，避免被覆盖
    expect(page.get_by_label("Model", exact=True)).to_have_value("Civic")
    expect(page.get_by_label("Year", exact=True)).to_have_value("2022")

    # 2. 修改数据并点击保存
    page.get_by_label("Model", exact=True).fill("Accord")
    page.get_by_label("Year", exact=True).fill("2023")
    page.get_by_role("button", name="Save changes").click()

    # 3. 关键修复：等待 URL 跳转回详情页（这证明保存请求已经处理完毕）
    expect(page).to_have_url(re.compile(r"/cars/\d+$"))

    # 4. 现在再断言详情页的内容（顺带把颜色也断言一下，更严谨）
    expect(page.locator("#car-model")).to_have_text("Accord")
    expect(page.locator("#car-year")).to_have_text("2023")
    expect(page.locator("#car-color")).to_have_text("White")

    # 5. 刷新页面，验证修改是否真的存到了数据库里（持久化）
    page.reload()
    expect(page.locator("#car-model")).to_have_text("Accord")
    expect(page.locator("#car-year")).to_have_text("2023")