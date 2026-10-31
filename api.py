from fastapi import FastAPI, UploadFile, File
import base64
from main import food_agent

app = FastAPI()

@app.post("/analyze-food")
def analyze_food(file: UploadFile = File(...)):
    image_bytes = file.file.read()

    print("Received:", file.filename)
    print("Size:", len(image_bytes))

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    image_url = f"data:{file.content_type};base64,{image_base64}"

    result = food_agent.invoke({
        "image_url": image_url,
        "food_name": "",
        "components": [],
        "nutrition": []
    })

    return result