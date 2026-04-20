# views.py
import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def lookup_barcode(request):
    barcode = request.query_params.get('barcode')

    if not barcode:
        return Response({'error': 'No barcode provided'}, status=400)

    chomp_url = f'https://chompthis.com/api/v2/food/branded/barcode.php'
    params = {
        'api_key': settings.CHOMP_API_KEY,
        'code': barcode,
    }

    try:
        res = requests.get(chomp_url, params=params)
        data = res.json()

        if not data.get('items'):
            return Response({'error': 'Product not found'}, status=404)

        item = data['items'][0]

        # return only what Flutter needs
        return Response({
            'name': item.get('name'),
            'brand': item.get('brand'),
            'barcode': item.get('barcode'),
            'calories': item.get('nf_calories'),
            'serving_size': item.get('nf_serving_size_qty'),
            'serving_unit': item.get('nf_serving_size_unit'),
            'ingredients': item.get('ingredients'),
        })

    except Exception as e:
        return Response({'error': str(e)}, status=500)