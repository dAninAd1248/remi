import requests
import json

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
    meals = data.get("meals")
    # meals = json.loads(meals)

    # meals returns a list of jsons
    counter = 0
    ingredients = [] 
    
    for i in range(1, 20):
        if meals[0][f"strIngredient{i}"] != "": 
          ingredients.append(meals[0][f"strIngredient{i}"] + " " + meals[0][f"strMeasure{i}"])
    
    instruction = meals[0]["strInstructions"]
    

    filter_result = {
       "instructions" : instruction, 
       "ingredients" : ingredients, 
    }
    
  

    # filter_result = {key: meals[0][key] for key in ["strInstructions", "strIngredient1"]}

    return filter_result


    



# print(search_meal_by_name("Lettuce"))
