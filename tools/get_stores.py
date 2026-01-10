from langchain.tools import tool
import os
import time
from pathlib import Path

from dotenv import load_dotenv
import googlemaps
from googlemaps.places import places_nearby, place
from urllib.parse import quote_plus

import asyncio
# import winsdk.windows.devices.geolocation as wdg

def _load_api_key():
    # Load .env (if present) then read environment variables
    load_dotenv()
    for name in ("GOOGLE_API_KEY", "PLACES_API_KEY", "API_KEY"):
        val = os.environ.get(name)
        if val:
            return val

    raise RuntimeError("API key not found in environment or .env file; set GOOGLE_API_KEY in .env or env")


def get_nearby_places(query, lat, long, radius=10000, max_results=1, rank_by_distance=False):
    """Search nearby places using the googlemaps client.

    - `query` is used as the `name` parameter (search for business names matching this).
    - `lat`, `long` are floats.
    - `radius` in meters (ignored when `rank_by_distance=True`).
    - `rank_by_distance`: when True, uses Places `rank_by=distance` (must omit `radius`).
    - Returns a list of place result dicts (up to `max_results`).
    """
    api_key = _load_api_key()
    gmaps = googlemaps.Client(key=api_key)
    location = (float(lat), float(long))

    results = []
    # initial request
    try:
        # Use 'name' parameter. If rank_by_distance is requested, call
        # places_nearby with rank_by='distance' and omit radius per API rules.
        if rank_by_distance:
            resp = places_nearby(gmaps, location=location, rank_by="distance", name=query)
        else:
            resp = places_nearby(gmaps, location=location, radius=int(radius), name=query)
    except Exception as e:
        raise RuntimeError(f"Places API request failed: {e}") from e

    results.extend(resp.get("results", []))

    # handle pagination - collect until we have max_results or no more pages
    while len(results) < max_results and resp.get("next_page_token"):
        next_token = resp["next_page_token"]
        # next_page_token may take a short time to become active
        time.sleep(2)
        try:
            resp = places_nearby(gmaps, page_token=next_token)
        except Exception as e:
            raise RuntimeError(f"Places API paging request failed: {e}") from e
        results.extend(resp.get("results", []))

    # Add a direct Google Maps URL for each place (use place_id when available,
    # otherwise fall back to coordinates or name search).
    for r in results:
        if r.get("maps_url"):
            continue

        # Try to fetch Place Details using place_id to get a canonical Maps URL or website
        place_id = r.get("place_id")
        if place_id:
            try:
                details = place(gmaps, place_id=place_id, fields=["url", "website"])
                detail_result = details.get("result", {})
                url_field = detail_result.get("url") or detail_result.get("website")
                if url_field:
                    r["maps_url"] = url_field
                    continue
            except Exception:
                # non-fatal — fall back to coordinates/name below
                pass

        geom = r.get("geometry", {}).get("location") or {}
        lat = geom.get("lat")
        lng = geom.get("lng")
        if lat is not None and lng is not None:
            r["maps_url"] = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
            continue

        # Fallback to name search
        name = r.get("name") or query
        r["maps_url"] = f"https://www.google.com/maps/search/?api=1&query={quote_plus(name)}"

    # Trim to requested max_results
    return results[:max_results]

async def get_coords():
    """Retrieves latitude and longitude using Windows Location Service."""
    # locator = wdg.Geolocator()
    # pos = await locator.get_geoposition_async()
    # return [pos.coordinate.latitude, pos.coordinate.longitude]
    return 18.21735686891109, -67.14221769364067

def get_location():
    """Runs the async function and handles permissions."""
    try:
        coords = asyncio.run(get_coords())
        #print(f"Latitude: {coords[0]}, Longitude: {coords[1]}")
        return coords
    except PermissionError:
        print("ERROR: You need to allow applications to access your location in Windows settings")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

@tool
def get_places(places: list[str], max_results=3):
    """
    Get nearby places for a list of store names.
    :param places: List of store names to search for.
    :param max_results: Maximum number of results to return per store.
    :return: Dictionary mapping store names to lists of nearby place results.
    """
    lat, long = get_location()
    all_results = {}
    for place in places:
        try:
            results = get_nearby_places(place, lat, long, max_results=max_results, radius=10000)
            keep_keys = [
                "business_status",
                "name",
                "international_phone_number",
                "place_id",
                "price_level",
                "rating",
                "types",
                "vicinity",
                "maps_url"
            ]

            filtered = []
            for r in results:
                out = {k: r.get(k) for k in keep_keys if k in r}
                filtered.append(out)

            all_results[place] = filtered
        except Exception as e:
            print(f'Error getting places for {place}:', e)
    return all_results

def main():
    from pprint import pprint
    results = get_places.invoke({"places": ["Walmart", "Target", "Best Buy"], "max_results": 3})
    pprint(results)

if __name__ == '__main__':
	main()