# import requests
# import json

# try:
#     response = requests.get("https://geolocation-db.com/json")
#     data = json.loads(response.text)
    
#     print("Your IP detail:")
#     print(f"IP: {data['IPv4']}")
#     print(f"City: {data['city']}")
#     print(f"Region: {data['state']}")
#     print(f"Country: {data['country_name']}")
#     print(f"Latitude/Longitude: {data['latitude']}, {data['longitude']}")

# except requests.exceptions.RequestException as e:
#     print(f"Error connecting to geolocation service: {e}")

#-------ip location. too general, marca san juan

#for windows
#pip install winsdk

import asyncio
import winsdk.windows.devices.geolocation as wdg

async def get_coords():
    """Retrieves latitude and longitude using Windows Location Service."""
    locator = wdg.Geolocator()
    pos = await locator.get_geoposition_async()
    return [pos.coordinate.latitude, pos.coordinate.longitude]

def get_location():
    """Runs the async function and handles permissions."""
    try:
        coords = asyncio.run(get_coords())
        print(f"Latitude: {coords[0]}, Longitude: {coords[1]}")
        return coords
    except PermissionError:
        print("ERROR: You need to allow applications to access your location in Windows settings")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

if __name__ == "__main__":
    get_location()

#---------------------works on my machine type-shit for windows


#for MAC 
#pip install pyobjc-framework-CoreLocation

import CoreLocation
from Foundation import NSObject, NSRunLoop, NSDate
import objc
import time

class LocationDelegate(NSObject):
    def init(self):
        self = objc.super(LocationDelegate, self).init()
        if self is None: return None
        self.location = None
        return self

    def locationManager_didUpdateLocations_(self, manager, locations):
        self.location = locations.lastObject()

    def locationManager_didFailWithError_(self, manager, error):
        print(f"Error: {error.localizedDescription()}")

def get_mac_location(timeout=10):
    """Retrieves (latitude, longitude) from macOS Core Location services."""
    manager = CoreLocation.CLLocationManager.alloc().init()
    delegate = LocationDelegate.alloc().init()
    manager.setDelegate_(delegate)
    
    # Request high accuracy (Macs use Wi-Fi triangulation)
    manager.setDesiredAccuracy_(CoreLocation.kCLLocationAccuracyBest)
    manager.startUpdatingLocation()

    # Wait for the delegate to receive a location fix
    start_time = time.time()
    while delegate.location is None and (time.time() - start_time) < timeout:
        NSRunLoop.currentRunLoop().runMode_beforeDate_(
            "NSDefaultRunLoopMode", 
            NSDate.dateWithTimeIntervalSinceNow_(0.1)
        )

    manager.stopUpdatingLocation()

    if delegate.location:
        coord = delegate.location.coordinate()
        return coord.latitude, coord.longitude
    return None

# Usage
coords = get_mac_location()
if coords:
    print(f"Latitude: {coords[0]}, Longitude: {coords[1]}")
else:
    print("Could not retrieve location.")


