import requests
from time import sleep
import json
import pandas as pd
from bs4 import BeautifulSoup as BSoup
from datetime import datetime

HEADER = {"X-Api-Key": "014709cfb534266769769522ac9ebaab"}
URL = "https://api.erasmusgeneration.org/api/static/v1/activities"

def fetch_country_codes():
    df_codes = pd.read_csv("country_codes.txt")[["name", "alpha-2"]]
    dic_codes = {}
    for _, row in df_codes.iterrows():
        dic_codes[row["alpha-2"]] = row["name"]
    return dic_codes

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

def process_data(data):
    columns = ["id", "url", "title", "description", "goal", "date_from", "date_to", "main_organiser", "participants",
               "country_of_origin", "type", "physical_location", "causes", "objectives", "sdgs"]
    df_activities = pd.DataFrame(data=[], columns=columns)

    df_causes = pd.DataFrame(data=[], columns=["identifier", "cause"])
    df_objectives = pd.DataFrame(data=[], columns=["identifier", "objective"])
    df_sdgs = pd.DataFrame(data=[], columns=["identifier", "sdg"])

    codes = fetch_country_codes()

    for index, identifier in enumerate(data["id"]):
        url = data["url"][index]
        title = data["title"][index]
        description = "\n".join(list(BSoup(data["description"][index], "html.parser").stripped_strings))
        goal = "\n".join(list(BSoup(data["goal"][index], "html.parser").stripped_strings))
        date_from = data["dates"][index]["start"]
        date_to = data["dates"][index]["end"]
        participants = ""
        main_organiser = data["organisers"][index][0]
        country_of_origin = codes[data["country"][index]]
        event_form = data["type"][index]

        if isinstance(data["physical_data"][index], dict):
            if len(data["physical_data"][index]["city"]) > 3:
                physical_location = f'{data["physical_data"][index]["city"]}, {codes[data["physical_data"][index]["country"]]}'
        else:
            physical_location = country_of_origin

        causes = [cause["name"] for cause in data["causes"][index]]
        causes.sort()
        objectives = [x for x in data["objectives"][index]]
        objectives.sort()
        sdgs = [sdg["name"] for sdg in data["sdgs"][index]]

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
            data=[[identifier, url, title, description, goal, date_from, date_to, main_organiser, participants,
                   country_of_origin, event_form, physical_location, ", ".join(causes), ", ".join(objectives), ", ".join(sdgs)]],
            columns=columns)
        df_activities = pd.concat([df_activities, df_activities_temp])

    df_activities.date_from = pd.to_datetime(df_activities.date_from, unit="s")
    df_activities.date_to = pd.to_datetime(df_activities.date_to, unit="s")

    df_activities.to_excel("activities.xlsx", encoding="utf-8", index=False)
    df_causes.to_excel("activities_causes.xlsx", encoding="utf-8", index=False)

    return df_activities, df_causes, df_objectives, df_sdgs


if __name__ == "__main__":
    # Download events and save the data into JSON
    get_activities()
    # Open the JSON and process the data
    with open("data_raw.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    activities, causes, objectives, sdgs = process_data(raw_data)

    for key in raw_data.keys():
        print(f"{key}: {raw_data[key][0]}")
