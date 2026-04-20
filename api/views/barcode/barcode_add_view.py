# api/views/barcode_product_view.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from ...models import Product, ProductBarcode

@api_view(['POST'])
@permission_classes([AllowAny])
def add_barcode_to_product(request, product_id):
    """
    Manually link a barcode to an existing product
    POST /api/products/{product_id}/add-barcode/
    Body: {"barcode": "012345678901"}
    """
    try:
        product = Product.objects.get(id=product_id)
        barcode = request.data.get('barcode')
        
        if not barcode:
            return Response({'error': 'Barcode required'}, status=400)
        
        # Check if barcode already exists
        if ProductBarcode.objects.filter(barcode=barcode).exists():
            return Response({
                'error': 'Barcode already linked to another product'
            }, status=400)
        
        # Create the barcode link
        ProductBarcode.objects.create(
            product=product,
            barcode=barcode,
            source='Manual'
        )
        
        return Response({
            'success': True,
            'message': 'Barcode added to product'
        })
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)