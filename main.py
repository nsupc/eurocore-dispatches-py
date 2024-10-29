from dataclasses import dataclass

import json
import os
import requests
import time

dispatch_url = "https://api.europeia.dev/dispatch"
queue_url = "https://api.europeia.dev/queue/dispatch/{}"


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

def check_job_completion(job_id: int, settings: Settings) -> bool:
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": settings.api_key
    }

    job_completed = False

    while not job_completed:
        status = requests.get(queue_url.format(job_id), headers=headers).json()

        match status["status"]:
            case "queued":
                print("Job in progress")
                time.sleep(5)
                continue
            case "success":
                print(f"Dispatch posting success: https://www.nationstates.net/page=dispatch/id={status['dispatch_id']}")
                return True
            case "failure":
                print(f"Dispatch posting failure: {status['error']}")
                return False

def upload_dispatch(filename: str, settings: Settings):
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": settings.api_key
    }

    with open(filename, "r", encoding="utf-8") as file_data:
        data = {
            "nation": settings.nation,
            "title": filename[:-4],
            "text": file_data.read(),
            "category": settings.category,
            "subcategory": settings.subcategory
        }

    try:
        job_id = requests.post(dispatch_url, headers=headers, json=data).json()["id"]
    except Exception as e:
        print(f"Error: {e}")
    else:
        print(f"Job {job_id} started, polling for completion")
        if check_job_completion(job_id, settings):
            os.remove(filename)

def main():
    settings = load_settings()

    for txt_file in [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.txt')]:
        upload_dispatch(txt_file, settings)

if __name__ == "__main__":
    main()