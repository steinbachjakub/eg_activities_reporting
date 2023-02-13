import requests
from time import sleep
import json
import pandas as pd
from bs4 import BeautifulSoup as BSoup
from datetime import datetime

HEADER = {"X-Api-Key": "014709cfb534266769769522ac9ebaab"}
URL = "https://api.erasmusgeneration.org/api/v1/activities"


def blank_content(response):
    if len(response["data"]) == 0:
        return True
    else:
        return False
def get_activities():
    current_page = 0
    data = {}

    while True:
        params = {"limit": "50", "page": f"{current_page}"}
        r = requests.get(url=URL, headers=HEADER, params=params).json()

        if blank_content(r):
            print(f"Reached last page ({current_page}), finishing data downloading.")
            break

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
    for key in raw_data.keys():
        print(f"{key}: {raw_data[key][0]}")

    columns = ["id", "url", "title", "description","goal", "date_from", "date_to", "main_organiser", "participants",
               "country_of_origin", "type", "causes"]
    df_activities = pd.DataFrame(data=[], columns=columns)

    df_causes = pd.DataFrame(data=[], columns=["identifier", "cause"])
    df_objectives = pd.DataFrame(data=[], columns=["identifier", "objective"])
    df_sdgs = pd.DataFrame(data=[], columns=["identifier", "sdg"])

    for index, identifier in enumerate(raw_data["id"]):
        url = raw_data["url"][index]
        title = raw_data["title"][index]
        description = "\n".join(list(BSoup(raw_data["description"][index], "html.parser").stripped_strings))
        goal = "\n".join(list(BSoup(raw_data["goal"][index], "html.parser").stripped_strings))
        date_from = datetime.fromtimestamp(raw_data["dates"][0]["start"]).strftime("%d/%m/%Y")
        date_to = datetime.fromtimestamp(raw_data["dates"][0]["end"]).strftime("%d/%m/%Y")
        participants = ""
        main_organiser = raw_data["organisers"][index][0]
        country_of_origin = raw_data["country"][index]
        event_form = raw_data["type"][index]
        causes = [cause["name"] for cause in raw_data["causes"][index]]
        causes.sort()
        objectives = [x for x in raw_data["objectives"][index]]
        objectives.sort()
        sdgs = [sdg["name"] for sdg in raw_data["sdgs"][index]]

        df_causes_temp = pd.DataFrame(
            data={"identifier": [identifier] * len(causes), "cause": causes}
        )
        df_causes = pd.concat([df_causes, df_causes_temp])

        df_objectives_temp = pd.DataFrame(
            data={"identifier": [identifier] * len(objectives), "objective": objectives}
        )
        df_objectives = pd.concat([df_objectives, df_objectives_temp])

        df_sdgs_temp = pd.DataFrame(
            data={"identifier": [identifier] * len(sdgs), "sdg": sdgs}
        )
        df_sdgs = pd.concat([df_sdgs, df_sdgs_temp])

        df_activities_temp = pd.DataFrame(
            data=[[identifier, url, title, description, goal, date_from, date_to, participants, main_organiser,
                   country_of_origin, event_form, ", ".join(causes)]],
            columns=columns)
        df_activities = pd.concat([df_activities, df_activities_temp])

    print("\n")
    print(df_objectives.objective.iloc[0])

