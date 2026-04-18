import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.serializers.product_serializer import UserLocationSerializer
from api.serializers.user_serializer import RegisterSerializer, UserProfileSerializer
from .products import products_info
from api.models import UserProfile

@api_view(['POST'])
@permission_classes([AllowAny])
def location_view(request):

    serializer = UserLocationSerializer(data = request.data)

    if serializer.is_valid():
        serializer.save()

        lat = serializer.validated_data['latitude']
        lon = serializer.validated_data['longitude']
        request.query_params._mutable = True
        request.query_params['latitude'] = lat
        request.query_params['longitude'] = lon

        return products_info(request)
    
    return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Account created successfully."},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    profile = request.user.profile

    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    if request.method == 'PATCH':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def geocode_zipcode(request):
    """
    Convert zipcode to lat/lng using Census Bureau API
    POST /api/location/geocode/
    Body: {"zipcode": "75701"}
    """
    zipcode = request.data.get('zipcode', '').strip()
    
    if not zipcode:
        return Response({'error': 'Zipcode required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Call Census Bureau Geocoding API
        url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'postalcode': zipcode,
            'country': 'US',
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'SavrrGroceryApp/1.0'  # Required by Nominatim
        }
            
        print(f'🗺️ Geocoding zipcode: {zipcode}')
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('result', {}).get('addressMatches'):
                match = data['result']['addressMatches'][0]
                coordinates = match['coordinates']
                
                return Response({
                    'success': True,
                    'latitude': coordinates['y'],
                    'longitude': coordinates['x'],
                    'zipcode': zipcode
                })
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid zipcode or no results found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'success': False,
                'error': 'Geocoding service unavailable'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
    except requests.exceptions.Timeout:
        return Response({
            'success': False,
            'error': 'Geocoding request timed out'
        }, status=status.HTTP_504_GATEWAY_TIMEOUT)
    except Exception as e:
        print(f'Geocoding error: {e}')
        return Response({
            'success': False,
            'error': 'Failed to geocode zipcode'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)