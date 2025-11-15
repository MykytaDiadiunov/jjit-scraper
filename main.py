import json
import time
from pathlib import Path

import pandas as pd
import requests

EXEL_PATH = "offers.xlsx"
OFFERS_JSON_PATH = "offers_urls.json"

URL_BASE = "https://justjoin.it/job-offer/"
BASE_API_URL = "https://api.justjoin.it/v1/offers"


def main():
    p = Path(OFFERS_JSON_PATH)
    with p.open("r", encoding="utf-8") as f:
        urls_to_parce = json.load(f)

        offers_data: list = []
        with requests.Session() as session:
            for url in urls_to_parce:
                try:
                    offer_data = get_offer_data_by_url(url, session)
                    offers_data.append(offer_data)
                except Exception as e:
                    print(f"main: {e}")
                finally:
                    print("main: wait for 1s before next page")
                    time.sleep(1)

def get_offer_data_by_url(url: str, session: requests.Session) -> dict:
    offer_id = url.split(URL_BASE)[-1]

    print(f"get_offer_data_by_url: starting scraping page with id: {offer_id}")

    response = session.get(f"{BASE_API_URL}/{offer_id}")
    response.raise_for_status()

    raw_offer_data = response.json()

    result = normalize_offer_response(raw_offer_data)

    print(
        f"get_offer_data_by_url: completed scraping page with title: {result.get('title')}"
    )
    return result

def normalize_offer_response(raw_offer_data: dict) -> dict:
    salary_data = get_salary_data(raw_offer_data)

    return {
        "title": raw_offer_data.get("title"),
        "experience_level": get_label(raw_offer_data.get("experienceLevel")),
        "salary_by": salary_data.get("unit"),
        "salary_value_from": salary_data.get("fromPln"),
        "salary_value_to": salary_data.get("toPln"),
        "contract_type": salary_data.get("label"),
        "company_city": raw_offer_data.get("city"),
        "working_time": get_label(raw_offer_data.get("workingTime")),
    }

def get_salary_data(raw_offer_data: dict) -> dict:
    employment_types = raw_offer_data.get("employmentTypes")
    salary_data = {}

    if employment_types and isinstance(employment_types, list) and len(employment_types) > 0:
        salary_data = employment_types[0]

    return salary_data

def get_label(obj: dict) -> any:
    return obj.get("label") if obj else None


if __name__ == "__main__":
    main()
