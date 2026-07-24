import os
import json
import requests
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

CUBE_API_URL = os.getenv("CUBE_API_URL")
CUBE_API_TOKEN = os.getenv("CUBE_API_TOKEN")

print("URL loaded:", CUBE_API_URL)
print("Token loaded:", CUBE_API_TOKEN[:20] if CUBE_API_TOKEN else "NONE FOUND", "...")


def query_cube(query):
    """Send a query to Cube.dev's REST API and return the result."""
    headers = {
        "Authorization": f"Bearer {CUBE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.get(
        f"{CUBE_API_URL}/load",
        params={"query": json.dumps(query)},
        headers=headers
    )
    print("Status code:", response.status_code)
    print("Response body:", response.text[:500])  # print first 500 chars for debugging
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    test_query = {
        "measures": [
            "fct_orders.total_revenue",
            "fct_orders.total_estimated_margin",
            "fct_orders.margin_pct"
        ],
        "dimensions": [
            "fct_orders.order_status"
        ]
    }

    result = query_cube(test_query)
    print("\nCube.dev connection successful!\n")
    print(result)