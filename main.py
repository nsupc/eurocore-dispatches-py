from dataclasses import dataclass

import json
import os
import requests

url = "https://api.europeia.dev/dispatch"


@dataclass
class Settings:
    api_key: str
    nation: str
    category: int
    subcategory: int


def load_settings() -> Settings:
    try:
        with open ("settings.json", "r") as file:
            settings = json.load(file)
    except Exception as e:
        print(f"Error: {e}")
        exit()

    if not "api_key" in settings:
        print("Error: Missing api_key")
        exit()

    if not "nation" in settings:
        print("Error: Missing nation")
        exit()

    if not "category" in settings:
        print("Error: Missing category")
        exit()

    if not "subcategory" in settings:
        print("Error: Missing subcategory")
        exit()

    return Settings(
        api_key=settings["api_key"],
        nation=settings["nation"],
        category=settings["category"],
        subcategory=settings["subcategory"]
    )

def upload_dispatch(filename: str, settings: Settings):
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": settings.api_key
    }

    with open(filename, "r") as file_data:
        data = {
            "nation": settings.nation,
            "title": filename[:-4],
            "text": file_data.read(),
            "category": settings.category,
            "subcategory": settings.subcategory
        }

    try:
        dispatch_id = requests.post(url, headers=headers, json=data).json()["id"]
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print(f"Uploaded {filename}: https://www.nationstates.net/page=dispatch/id={dispatch_id}")
        os.remove(filename)

def main():
    settings = load_settings()

    for txt_file in [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.txt')]:
        upload_dispatch(txt_file, settings)

if __name__ == "__main__":
    main()