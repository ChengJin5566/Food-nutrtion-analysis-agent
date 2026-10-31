import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

USDA_API_KEY = os.getenv("USDA_API_KEY")

BASE_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"


def format_food(food):

    nutrients = food.get("foodNutrients", [])

    nutrition = {
        "calories": None,
        "protein_g": None,
        "carbohydrates_g": None,
        "fat_g": None
    }

    for nutrient in nutrients:

        name = nutrient.get("nutrientName")
        value = nutrient.get("value")

        if name == "Energy":
            nutrition["calories"] = value

        elif name == "Protein":
            nutrition["protein_g"] = value

        elif name == "Carbohydrate, by difference":
            nutrition["carbohydrates_g"] = value

        elif name == "Total lipid (fat)":
            nutrition["fat_g"] = value

    return {
        "name": food.get("description"),
        "fdc_id": food.get("fdcId"),
        "nutrition": nutrition
    }

@tool
def get_nutrition(food_name: str):
    """
    Search the USDA FoodData Central database for nutrition information
    based on a food name.
    """

    params = {
        "api_key": USDA_API_KEY,
        "query": food_name,
        "pageSize": 5
    }

    response = requests.get(BASE_URL, params=params)

    response.raise_for_status()

    data = response.json()

    foods = data.get("foods", [])

    if not foods:
        return None

    formatted_foods = []

    for food in foods:
        formatted_foods.append(format_food(food))

    return formatted_foods


if __name__ == "__main__":

    food_name = input("Enter food name: ")

    result = get_nutrition.invoke({
        "food_name": food_name
    })

    if result is None:
        print("No food found.")
    else:
        for i, food in enumerate(result, start=1):
            print(f"\n--- Result {i} ---")
            print(f"Food: {food['name']}")
            print(f"Food_ID: {food['fdc_id']}")

            nutrition = food["nutrition"]

            print(f"Calories: {nutrition['calories']} kcal")
            print(f"Protein: {nutrition['protein_g']} g")
            print(f"Carbohydrates: {nutrition['carbohydrates_g']} g")
            print(f"Fat: {nutrition['fat_g']} g")