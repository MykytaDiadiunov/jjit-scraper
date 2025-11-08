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
                print(e)
            finally:
                time.sleep(2)

        offers_df = pd.DataFrame(offers_data)

        offers_df.to_excel(EXEL_PATH, index=False)


def get_offer_data_by_url(url: str) -> dict:
    offer_id = url.split(URL_BASE)[-1]

    response: requests.Response = requests.get(f"{BASE_API_URL}/{offer_id}")
    if response.status_code != 200:
        raise Exception(f"url with id {offer_id} return a error {response.status_code}")

    response_in_json = response.json()

    return {
        "title": response_in_json.get("title"),
        **response_in_json.get("employmentTypes")[0],
    }


if __name__ == "__main__":
    main()
