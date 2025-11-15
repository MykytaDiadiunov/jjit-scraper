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
        for url in urls_to_parce:
            try:
                offer_data = get_offer_data_by_url(url)
                offers_data.append(offer_data)
            except Exception as e:
                print(f"main: {e}")
            finally:
                print("main: wait for 1s before next page")
                time.sleep(1)

        offers_df = pd.DataFrame(offers_data)

        offers_df.to_excel(EXEL_PATH, index=False)
        print("main: finished and creating offers Excel file")


def get_offer_data_by_url(url: str) -> dict:
    offer_id = url.split(URL_BASE)[-1]

    print(f"get_offer_data_by_url: starting scraping page with id: {offer_id}")

    response: requests.Response = requests.get(f"{BASE_API_URL}/{offer_id}")
    if response.status_code != 200:
        raise Exception(
            f"url with id {offer_id} returned an error {response.status_code}"
        )

    response_in_json = response.json()

    salary_data = response_in_json.get("employmentTypes")[0]

    result = {
        "title": response_in_json.get("title"),
        "experience_level": response_in_json.get("experienceLevel").get("label"),
        "salary_by": salary_data.get("unit"),
        "salary_value_from": salary_data.get("fromPln"),
        "salary_value_to": salary_data.get("toPln"),
        "contract_type": salary_data.get("label"),
        "company_city": response_in_json.get("city"),
        "working_time": response_in_json.get("workingTime").get("label"),
    }

    print(
        f"get_offer_data_by_url: completed scraping page with title: {result.get('title')}"
    )
    return result


if __name__ == "__main__":
    main()
