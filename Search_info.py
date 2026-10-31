from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup


def get_myfcd_nutrition(url):

    parts = url.split("/")
    parts[-4] = "-1"
    url = "/".join(parts)

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)

        page = browser.new_page()

        page.goto(
            url,
            wait_until="networkidle"
        )

        html = page.content()

        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    tables = soup.find_all("table")
    nutrition_table = tables[2]

    nutrition = {}

    rows = nutrition_table.find_all("tr")[1:]

    for row in rows:

        cells = row.find_all(["th", "td"])

        values = [
            cell.get_text(" ", strip=True)
            for cell in cells
        ]

        if len(values) < 3:
            continue

        nutrient = values[0]
        unit = values[1]
        value = values[2]

        nutrition[nutrient] = {
            "value": value,
            "unit": unit
        }

    required_nutrients = [
        "Energy",
        "Protein",
        "Fat",
        "Carbohydrate"
    ]

    is_basic_nutrition = all(
        nutrient in nutrition
        for nutrient in required_nutrients
    )

    return {
        "nutrition": nutrition,
        "is_basic_nutrition": is_basic_nutrition
    }


def search_myfcd(query):

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)

        page = browser.new_page()

        page.goto(
            "https://myfcd.moh.gov.my/",
            wait_until="networkidle"
        )

        # Search
        search_box = page.locator("#search")
        search_box.fill(query)

        # Click Search
        page.locator("#myBtn").click()

        # Wait for results
        page.wait_for_timeout(3000)

        # Find food detail links
        links = page.locator(
            'a[href*="detail_product"]'
        )

        foods = []

        for i in range(0, links.count(), 2):

            food_id = links.nth(i)
            food_name = links.nth(i + 1)

            foods.append({
                "food_id": food_id.inner_text(),
                "name": food_name.inner_text(),
                "url": food_name.get_attribute("href")
            })

        browser.close()

    if not foods:
        return None

    return foods


if __name__ == "__main__":

    query = input("Enter food name: ")

    foods = search_myfcd(query)

    if foods is None:

        print("No MyFCD results found.")

    else:

        print("\n===== RESULTS =====")

        for food in foods:

            print(f"\nFood ID: {food['food_id']}")
            print(f"Food: {food['name']}")

        food_id = input("\nEnter Food ID: ")

        selected_food = None

        for food in foods:

            if food["food_id"] == food_id:
                selected_food = food
                break

        if selected_food is None:

            print("Food ID not found.")

        else:

            nutrition = get_myfcd_nutrition(
                selected_food["url"]
            )

            print("\n===== NUTRITION =====")

            for nutrient, data in nutrition["nutrition"].items():

                print(
                    f"{nutrient}: "
                    f"{data['value']} "
                    f"{data['unit']}"
                )