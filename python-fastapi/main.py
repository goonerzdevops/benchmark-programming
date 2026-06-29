from fastapi import FastAPI
from pydantic import BaseModel
import hashlib
import time

app = FastAPI()

class Item(BaseModel):
    numeric_value: float
    string_data: str

class InputData(BaseModel):
    items: list[Item]

@app.post("/complex-transform")
async def complex_transform(data: InputData):
    start_time = time.time()

    # 1. Validasi input (Pydantic handles this)

    numeric_values = []
    all_strings = []

    for item in data.items:
        numeric_values.append(item.numeric_value)
        all_strings.append(item.string_data)

    # 2. Agregasi & Transformasi Data
    # Hitung rata-rata dari semua nilai numerik
    avg_numeric = sum(numeric_values) / len(numeric_values) if numeric_values else 0

    # Gabungkan semua string menjadi satu string panjang, lalu hash
    combined_string = "".join(all_strings)
    hashed_string = hashlib.sha256(combined_string.encode()).hexdigest()

    # Hitung nilai baru untuk setiap objek dan urutkan
    transformed_items = []
    for item in data.items:
        new_value = (item.numeric_value * 1.5) + (len(combined_string) / 2)
        transformed_items.append({"original_numeric": item.numeric_value, "original_string": item.string_data, "new_value": new_value})

    # Urutkan array objek berdasarkan nilai baru
    transformed_items.sort(key=lambda x: x["new_value"])

    end_time = time.time()
    processing_time = end_time - start_time

    # 3. Output
    return {
        "average_numeric_value": avg_numeric,
        "hashed_combined_string": hashed_string,
        "transformed_and_sorted_items": transformed_items,
        "server_processing_time": processing_time
    }
