import requests
from time import sleep
import json


def blank_content(response):
    if len(response["data"]) == 0:
        return True
    else:
        return False
def get_activities():
    HEADER = {"X-Api-Key": "014709cfb534266769769522ac9ebaab"}
    URL = "https://api.erasmusgeneration.org/api/static/v1/activities"
    current_page = 0
    data = {}

    for current_page in range(200):
        params = {"limit": "50", "page": f"{current_page}"}
        r = requests.get(url=URL, headers=HEADER, params=params).json()

        # if blank_content(r):
        #     print(f"Reached last page ({current_page}), finishing data downloading.")
        #     break

        for item in r["data"]:
            if len(data.keys()) == 0:
                for key in item.keys():
                    data[key] = [item[key]]
            else:
                for key in item.keys():
                    data[key].append(item[key])

        current_page += 1
        if current_page % 100 == 0:
            print(f"Checked page {current_page}.")
        sleep(0.2)

    with open("data_raw.json", "w") as output_file:
        json.dump(data, output_file)


if __name__ == "__main__":
    # get_activities()
    with open("data_raw.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    print(len(raw_data.keys()))
