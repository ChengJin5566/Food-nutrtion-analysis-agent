from select_food import select_food_batch

def calculate_nutrition(results):

    calculated_results = []

    for component in results:

        portion_g = component["portion_g"]
        nutrition = component["nutrition"]["nutrition"]

        calculated_nutrition = {}

        for nutrient, data in nutrition.items():

            value = float(data["value"])
            unit = data["unit"]

            actual_value = value * portion_g / 100

            calculated_nutrition[nutrient] = {
                "value": actual_value,
                "unit": unit
            }

        calculated_results.append({
            "component": component["component"],
            "portion_g": portion_g,
            "food": component["food"],
            "nutrition": calculated_nutrition
        })

    return calculated_results

if __name__ == "__main__":
    components = []

    while True:
        name = input("\nEnter food name (or 'done'): ")

        if name.lower() == "done":
            break

        portion_g = float(
            input("Enter portion (g): ")
        )

        components.append({
            "name": name,
            "portion_g": portion_g
        })

    if not components:
        print("No foods entered.")
        exit()

    print("\n===== SELECTING FOOD =====")

    results = select_food_batch(
        components
    )

    results = calculate_nutrition(
        results
    )

    print("\n===== RESULTS =====")

    for i, result in enumerate(results, start=1):

        print(f"\n--- Component {i} ---")
        print(f"Component: {result['component']}")
        print(f"Portion: {result['portion_g']} g")
        print(f"Food: {result['food']['name']}")
        print(f"Food ID: {result['food']['food_id']}")

        print("\nNutrition:")

        for nutrient, data in result["nutrition"].items():

            print(
                f"{nutrient}: "
                f"{data['value']} "
                f"{data['unit']}"
            )