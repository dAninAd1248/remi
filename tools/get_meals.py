#ingredient = "chicken_breast"
import pandas as pd
import random
from langchain.tools import tool

@tool
def main_ingredient(ingredient):
    """
    This tool goal is tool is to find a meal with a random ingredient given by the user.
    If ingredient not in english translate to english. 
    If the ingredient has spaces, replace the space with an underscore. 
    """
    try:
        url = "https://www.themealdb.com/api/json/v1/1/filter.php?i="+ingredient
        data = pd.read_json(url)
        df = pd.json_normalize(data["meals"])

        rng = random.randint(0, len(df))
        return str(df.loc[rng,"strMeal"])
    except Exception as e:
        return f"Error retrieving meal: {e}. Ingredients probably don't exist."


# print(main_ingredient("Tomato"))