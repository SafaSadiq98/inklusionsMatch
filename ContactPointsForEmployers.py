# imports

import requests
import pandas as pd


def get_contact_details(postcode):
    # Define apis, headers and postcode for fetching data

    api_url_zipcode = "https://kontaktsuche.bih.de/api/post-codes"
    api_url_institutes = "https://kontaktsuche.bih.de/api/v2/institutes"
    api_key = "YR39qInUOsPpv-IbhpE-cl7--xwblf4PX_TQezxxgQA"
    data_initial_institute_type = "7"

    headers_zipcodes = {"X-Auth-Token": api_key, "Content-Type": "application/json"}
    headers_institutes = {"X-Auth-Token": api_key, "Content-Type": "application/json"}

    # Search for zip code id using post code
    query_url = f"{api_url_zipcode}?zip_code={postcode}"
    response = requests.get(query_url, headers=headers_zipcodes)
    if response.status_code == 200:
        data = response.json()
        zip_code_id = data['data'][0]['zip_code_id']
    else:
        return f"Status code: {response.status_code}", f"Status text: {response.text}"

    # Search for contact points using zip code id
    query_url = f"{api_url_institutes}?type_id={data_initial_institute_type}&zip_code_id={zip_code_id}"
    response = requests.get(query_url, headers=headers_institutes)
    if response.status_code == 200:
        data = response.json()  # Assuming the API returns JSON data
    else:
        return f"Status code: {response.status_code}", f"Status text: {response.text}"

    # data for institutes
    institute = pd.DataFrame(columns=['name', 'street', 'zip_code', 'city', 'show_map_link', 'website'])
    for i in range(len(data["data"])):
        institute.loc[i] = data["data"][i]["visitor_address"]
        institute['website'][i] = data["data"][i]["website"]
        institute['name'][i] = data["data"][i]["name"]
        # institute['description'][i] = data["data"][i]["description"]
    institute = institute.drop(columns=["show_map_link"])

    # data for contact points in the institutes
    contacts = pd.DataFrame(columns=['name', 'id', 'salutation', 'firstname', 'lastname', 'email', 'phone_number'])
    for i in range(len(data["data"])):
        institiute_name = {'name': institute['name'][i]}
        for j in range(len(data["data"][i]["contacts"])):
            data["data"][i]["contacts"][j] = {**institiute_name, **data["data"][i]["contacts"][j]}
            contacts.loc[i] = data["data"][i]["contacts"][j]
    contacts = contacts.drop(columns=['id'])

    contact_points = pd.merge(institute, contacts, on='name', how='left')

    return data, contact_points
