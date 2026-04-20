import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from api.serializers.product_serializer import UserLocationSerializer
from api.serializers.user_serializer import RegisterSerializer
from api.services.location.geocode import LocationService  
from .grocery.products import products_info
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


@api_view(['POST'])
@permission_classes([AllowAny])
def geocode_zipcode(request):
    """
    Convert zipcode to lat/lng using Zippopotam API
    POST /api/location/geocode/
    Body: {"zipcode": "75701"}
    """
    zipcode = request.data.get('zipcode')
    
    # Use service to handle geocoding logic
    result = LocationService.geocode_zipcode(zipcode)
    
    if result['success']:
        return Response({
            'success': True,
            'latitude': result['latitude'],
            'longitude': result['longitude'],
            'zipcode': result['zipcode']
        })
    else:
        return Response(
            {
                'success': False,
                'error': result['error']
            },
            status=result['status_code']
        )