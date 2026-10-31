import requests

DATABASES = [
    (
        "current",
        "https://myfcd.moh.gov.my/myfcdcurrent/index.php/ajax/datatable_data"
    ),
    (
        "myfcd97",
        "https://myfcd.moh.gov.my/myfcd97/index.php/ajax/datatable_data"
    ),
    (
        "industri",
        "https://myfcd.moh.gov.my/myfcdindustri/static/DataTables-1.10.12/examples/server_side/scripts/server_processing.php"
    ),
]


def get_all_foods():

    all_foods = []

    for database, url in DATABASES:

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        for food in data["data"]:

            all_foods.append({
                "database": database,
                "food_id": food[0],
                "name": food[1]
            })

    return all_foods


