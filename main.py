import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from select_food import select_food_batch
from calculate_nutrition import calculate_nutrition

load_dotenv()

class FoodComponent(TypedDict):
    name: str
    portion_g: float

class FoodAnalysis(TypedDict):
    food_name: str
    components: list[FoodComponent]

class FoodState(TypedDict):
    image_url: str
    food_name: str
    components: list[FoodComponent]
    nutrition: list

model = ChatOpenAI(
    model="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    timeout=120,
    max_retries=5,
)

def parse_json_response(content: str):

    content = content.strip()

    start = content.find("{")
    end = content.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model response")

    content = content[start:end + 1]

    return json.loads(content)

def analyze_food(state: FoodState):

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": """
Analyze this food image.

Identify:
1. The overall dish.
2. The visible food ingredient.
3. The estimated portion of each component in grams.

Only identify raw food components that are visibly present.
Do not assume ingredients that cannot be seen.

Return ONLY JSON.

Example:

{
    "food_name": "Hainanese chicken rice",
    "components": [
        {
            "name": "chicken breast",
            "portion_g": 150
        },
        {
            "name": "white rice",
            "portion_g": 200
        }
    ]
}
"""
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": state["image_url"]
                }
            }
        ]
    )

    try:
        response = model.invoke([message])
    except Exception as e:
        print("Model error:", e)
        raise

    print("MODEL RESPONSE:")
    print(repr(response.content))

    data = parse_json_response(response.content)

    return {
        "food_name": data["food_name"],
        "components": data["components"]
    }

def get_food_nutrition(state: FoodState):

    results = select_food_batch(
        state["components"]
    )

    results = calculate_nutrition(
        results
    )

    return {
        "nutrition": results
    }

graph = StateGraph(FoodState)

graph.add_node("analyze_food", analyze_food)
graph.add_node("get_food_nutrition", get_food_nutrition)

graph.add_edge(START, "analyze_food")
graph.add_edge("analyze_food", "get_food_nutrition")
graph.add_edge("get_food_nutrition", END)
food_agent = graph.compile()


if __name__ == "__main__":

    image_url = input("Enter image URL: ")

    result = food_agent.invoke({
        "image_url": image_url,
        "food_name": "",
        "components": [],
        "nutrition": []
    })

    print("\nFinal state:")
    print(result)

    total_nutrition = {}

    for i, food in enumerate(result["nutrition"], start=1):

        print(f"\n--- Component {i} ---")
        print(f"Component: {food['component']}")
        print(f"Estimated portion: {food['portion_g']} g")

        food_info = food["food"]
        nutrition = food["nutrition"]

        print(f"Food: {food_info['name']}")
        print(f"Food ID: {food_info['food_id']}")

        print("Nutrition:")

        for nutrient, data in nutrition.items():

            print(
                f"{nutrient}: "
                f"{data['value']} "
                f"{data['unit']}"
            )

            if nutrient not in total_nutrition:
                total_nutrition[nutrient] = {
                    "value": 0,
                    "unit": data["unit"]
                }

            total_nutrition[nutrient]["value"] += data["value"]

    print("\n\n===== FINAL NUTRITION REPORT =====")

    for nutrient, data in total_nutrition.items():

        print(
            f"{nutrient}: "
            f"{data['value']} "
            f"{data['unit']}"
        )
