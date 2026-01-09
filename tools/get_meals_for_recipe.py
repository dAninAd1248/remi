import requests

def search_meal_by_name(meal_name):
    """
    Search for meals by name using TheMealDB API.

    :param meal_name: str, name of the meal to search for
    :return: list of meals or None if not found
    """
    url = "https://www.themealdb.com/api/json/v1/1/search.php"
    params = {"s": meal_name}

    response = requests.get(url, params=params)
    response.raise_for_status()  # raises error for bad HTTP responses

    data = response.json()
    return data.get("meals")


print(search_meal_by_name("Fettucine alfredo"))
