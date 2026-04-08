from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from api.serializers.serializer import UserLocationSerializer
from .products import products_info

@api_view(['POST'])
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