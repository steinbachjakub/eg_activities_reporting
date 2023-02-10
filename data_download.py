import requests
from time import sleep
from bs4 import BeautifulSoup
import json



def blank_content(response):
    if len(response["data"]) == 0:
        return True
    else:
        return False
def get_activities():
    HEADER = {"X-Api-Key": "014709cfb534266769769522ac9ebaab"}
    URL = "https://api.erasmusgeneration.org/api/v1/activities"
    current_page = 0
    data = {}

    while True:
        params = {"limit": "50", "page": f"{current_page}"}
        r = requests.get(url=URL, headers=HEADER, params=params).json()

        if blank_content(r):
            print(f"Reached last page, finishing data downloading.")
            break

        for item in r["data"]:
            if len(data.keys()) == 0:
                for key in item.keys():
                    data[key] = [item[key]]
            else:
                for key in item.keys():
                    data[key].append(item[key])

        current_page += 1
        if current_page % 50 == 0:
            print(f"Checked page {current_page}.")
        sleep(0.2)

    data_json = json.dumps(data)
    with open("data_raw.json", "w") as f:
        json.dumps(data, f)

if __name__ == "__main__":
    get_activities()
    with open("data_raw.csv", "r", encoding="utf-8") as f:
        data = f.read()

    print(json.loads(data))