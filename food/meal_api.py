# meal_api.py

import requests

class TheMealDBAPI:
    BASE_URL = "https://www.themealdb.com/api/json/v1/1/"

    def search_meals(self, query):
        """Search for meals by name or ingredient."""
        url = f"{self.BASE_URL}search.php?s={query}"
        response = requests.get(url)
        return response.json()

    def get_meal_details(self, meal_id):
        """Get details of a specific meal by ID."""
        url = f"{self.BASE_URL}lookup.php?i={meal_id}"
        response = requests.get(url)
        return response.json()
