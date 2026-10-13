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

    # 点击编辑，并【强制等待】URL 变成 /cars/1/edit 这种格式
    page.get_by_role("link", name="Edit car").click()
    expect(page).to_have_url(re.compile(r"/cars/\d+/edit"), timeout=15000)
    
    # 回到最稳定的 label 定位法（不要用 input#car-model）
    page.get_by_label("Model", exact=True).fill("Accord")
    page.get_by_label("Year", exact=True).fill("2023")
    
    # 点击保存
    page.get_by_role("button", name="Save changes").click()
    
    # 等待保存成功后，URL 变回详情页
    expect(page).to_have_url(re.compile(r"/cars/\d+$"), timeout=15000)
    
    # 刷新页面，强制从数据库拉取最新数据
    page.reload()
    
    # 此时详情页的 #car-model 元素应该存在，且内容为 Accord
    expect(page.locator("#car-model")).to_have_text("Accord", timeout=15000)
    expect(page.locator("#car-year")).to_have_text("2023", timeout=15000)

    page.reload()
    expect(page.locator("#car-model")).to_have_text("Accord")
    expect(page.locator("#car-year")).to_have_text("2023")