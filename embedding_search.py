from sentence_transformers import SentenceTransformer
from food_database import get_all_foods


model = SentenceTransformer("all-MiniLM-L6-v2")


def find_candidates(query, foods):

    food_names = [
        food["name"]
        for food in foods
    ]

    query_embedding = model.encode(query)
    food_embeddings = model.encode(food_names)

    scores = food_embeddings @ query_embedding

    threshold = 0.55

    candidates = []

    for index in scores.argsort()[::-1]:

        if scores[index] >= threshold:
            candidates.append(foods[index])

            if len(candidates) == 3:
                break

    return candidates


if __name__ == "__main__":

    query = input("Enter food name: ")

    foods = get_all_foods()

    candidates = find_candidates(
        query,
        foods
    )

    print("\n===== CANDIDATES =====")

    for food in candidates:

        print(
            f"{food['food_id']} - "
            f"{food['name']}"
        )