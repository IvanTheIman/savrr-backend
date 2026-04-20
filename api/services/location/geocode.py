
import requests


class LocationService:
    """
    function that attempts to connect to Zippo API to convert zipcode to approximate lat and lan
    """
    
    GEOCODING_API_URL = 'https://api.zippopotam.us/us'
    TIMEOUT = 10
    
    @staticmethod
    def geocode_zipcode(zipcode):
        if not zipcode or not zipcode.strip():
            return {
                'success': False,
                'error': 'Zipcode required',
                'status_code': 400
            }
        
        zipcode = zipcode.strip()
        
        try:
            url = f'{LocationService.GEOCODING_API_URL}/{zipcode}'
            print(f'Geocoding zipcode: {zipcode}')
            
            response = requests.get(url, timeout=LocationService.TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                
                # Get coordinates from first place
                if 'places' in data and len(data['places']) > 0:
                    place = data['places'][0]
                    latitude = float(place['latitude'])
                    longitude = float(place['longitude'])
                    
                    print(f'Geocoded to: {latitude}, {longitude}')
                    
                    return {
                        'success': True,
                        'latitude': latitude,
                        'longitude': longitude,
                        'zipcode': zipcode,
                        'status_code': 200
                    }
                else:
                    print(f'No results for zipcode: {zipcode}')
                    return {
                        'success': False,
                        'error': 'Invalid zipcode',
                        'status_code': 404
                    }
                    
            elif response.status_code == 404:
                print(f'Invalid zipcode: {zipcode}')
                return {
                    'success': False,
                    'error': 'Invalid zipcode',
                    'status_code': 404
                }
            else:
                print(f'Geocoding API returned: {response.status_code}')
                return {
                    'success': False,
                    'error': 'Geocoding service unavailable',
                    'status_code': 503
                }
                
        except requests.exceptions.Timeout:
            print('Geocoding request timed out')
            return {
                'success': False,
                'error': 'Geocoding request timed out',
                'status_code': 504
            }
        except Exception as e:
            print(f'Geocoding error: {e}')
            return {
                'success': False,
                'error': 'Failed to geocode zipcode',
                'status_code': 500
            }