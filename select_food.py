import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from food_database import get_all_foods
from embedding_search import find_candidates
from Search_info import search_myfcd, get_myfcd_nutrition

load_dotenv()

model = ChatOpenAI(
    model="nvidia/nemotron-nano-12b-v2-vl:free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def choose_best_food_batch(components):

    prompt = """
Choose the best MyFCD food for each user food.

Return ONLY valid JSON.
Do not include markdown or explanations.

Format:
{
    "0": 2,
    "1": 0,
    "2": 1
}

The key is the component number.
The value is the candidate index.
"""

    for i, component in enumerate(components):

        prompt += f"\n\nComponent {i}: {component['name']}\n"

        for j, food in enumerate(component["candidates"]):
            prompt += f"{j}: {food['name']}\n"

    response = model.invoke(prompt)
    content = response.content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("Invalid AI response:")
        print(repr(content))
        return None

def select_food_batch(components):
    foods = get_all_foods()
    prepared_components = []

    for component in components:

        candidates = find_candidates(
            component["name"],
            foods
        )

        if not candidates:
            prepared_components.append({
                "name": component["name"],
                "portion_g": component["portion_g"],
                "candidates": []
            })

            continue

        prepared_components.append({
            "name": component["name"],
            "portion_g": component["portion_g"],
            "candidates": candidates
        })

    valid_components = [
        component
        for component in prepared_components
        if component["candidates"]
    ]

    if not valid_components:
        return []

    selections = choose_best_food_batch(
        valid_components
    )

    if selections is None:
        return []

    results = []

    for i, component in enumerate(valid_components):
        index = selections[str(i)]
        best_food = component["candidates"][index]
        myfcd_foods = search_myfcd(
            best_food["name"]
        )

        if not myfcd_foods:
            continue

        food = myfcd_foods[0]
        nutrition = get_myfcd_nutrition(
            food["url"]
        )
        results.append({
            "component": component["name"],
            "portion_g": component["portion_g"],
            "food": food,
            "nutrition": nutrition
        })

    return results

if __name__ == "__main__":
    foods = get_all_foods()
    components = []

    while True:
        query = input("\nEnter food name (or 'done'): ")

        if query.lower() == "done":
            break

        candidates = find_candidates(
            query,
            foods
        )

        if not candidates:
            print("No suitable food candidate found.")
            continue

        components.append({
            "name": query,
            "candidates": candidates
        })

    if not components:
        print("No foods entered.")
        exit()

    print("\n===== AI SELECTING =====")
    selections = choose_best_food_batch(
        components
    )

    if selections is None:
        exit()

    print("\n===== RESULTS =====")

    for i, component in enumerate(components):
        index = selections[str(i)]
        best_food = component["candidates"][index]

        print(f"\nInput: {component['name']}")
        print(f"Selected: {best_food['name']}")
        print(f"Food ID: {best_food['food_id']}")

        myfcd_foods = search_myfcd(
            best_food["name"]
        )

        if not myfcd_foods:
            print("No MyFCD result found.")
            continue

        food = myfcd_foods[0]
        nutrition = get_myfcd_nutrition(
            food["url"]
        )

        print("\nNutrition:")

        for nutrient, data in nutrition["nutrition"].items():
            print(
                f"{nutrient}: "
                f"{data['value']} "
                f"{data['unit']}"
            )