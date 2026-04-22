from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response 
from rest_framework import status 
from django.db.models import Q 

from api.models import Product, ProductBarcode, Store
from api.serializers.product_serializer import BarcodeLookupSerializer
from api.services.barcode.barcode_fetch import OpenFoodFactsService


# Hardcoded barcode mappings - Map barcodes to existing product names in your database
HARDCODED_BARCODES = {
    '4011': {
        'name': 'bananas',  # Make sure you have a product named "Banana" in your database
        'variant_name': 'Banana (PLU 4011)',
        'source': 'hardcoded'
    },
    '4016': {
        'name': 'red delicious apple',  # Make sure you have a product named "Apple" in your database
        'variant_name': 'Red Delicious Apple (PLU 4016)',
        'source': 'hardcoded'
    },
}


@api_view(['GET'])
@permission_classes([AllowAny])
def barcode_lookup_view(request, barcode):
    """
    Lookup product by barcode - links to existing products only
    GET /api/products/barcode/{barcode}/?store_id=1
    """
    store_id = request.GET.get('store_id')
    store = None
    
    if store_id:
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Store not found'
            }, status = status.HTTP_404_NOT_FOUND)
    
    # Step 1: Check if barcode already exists in ProductBarcode table
    try:
        product_barcode = ProductBarcode.objects.select_related('product').get(barcode=barcode)
        product = product_barcode.product
        
        serializer = BarcodeLookupSerializer(product, context={'store': store})
        
        return Response({
            'success': True,
            'supported': True,
            'product': serializer.data,
            'source': 'database'
        })
        
    except ProductBarcode.DoesNotExist:
        # Step 2: Check hardcoded barcodes BEFORE hitting external API
        if barcode in HARDCODED_BARCODES:
            print(f"🔒 Found hardcoded barcode: {barcode}")
            
            hardcoded_data = HARDCODED_BARCODES[barcode]
            product_name = hardcoded_data['name']
            
            # Try to find existing product with matching name
            existing_product = Product.objects.filter(
                Q(name__iexact=product_name)
            ).first()
            
            if existing_product:
                # Match found - link barcode to existing product
                print(f"✅ Linked hardcoded barcode {barcode} to product: {existing_product.name}")
                
                ProductBarcode.objects.create(
                    product=existing_product,
                    barcode=barcode,
                    variant_name=hardcoded_data.get('variant_name', product_name),
                    source=hardcoded_data.get('source', 'hardcoded')
                )
                
                serializer = BarcodeLookupSerializer(existing_product, context={'store': store})
                
                return Response({
                    'success': True,
                    'supported': True,
                    'product': serializer.data,
                    'source': 'hardcoded',
                    'message': 'Hardcoded barcode linked to product'
                })
            else:
                # Product doesn't exist in database
                return Response({
                    'success': True,
                    'supported': False,
                    'message': f'Product "{product_name}" not found in database. Please add it first.',
                    'barcode': barcode
                }, status=status.HTTP_200_OK)
        
        # Step 3: Barcode not hardcoded - try Open Food Facts
        print(f"Barcode {barcode} not found in database or hardcoded list. Checking Open Food Facts...")
        
        external_data = OpenFoodFactsService.fetch_product(barcode)
        
        if external_data:
            # Step 4: Found in Open Food Facts - try to match EXISTING product only
            product_name = external_data['name']
            
            # Try to find existing product with similar name
            existing_product = Product.objects.filter(
                Q(name__iexact=product_name) |  # Exact match (case insensitive)
                Q(name__icontains=product_name.split()[0]) if product_name.split() else Q()  # First word match
            ).first()
            
            if existing_product:
                # Match found - link barcode to existing product
                print(f"✅ Matched barcode {barcode} to existing product: {existing_product.name}")
                
                ProductBarcode.objects.create(
                    product=existing_product,
                    barcode=barcode,
                    variant_name=product_name,
                    source='Open Food Facts'
                )
                
                serializer = BarcodeLookupSerializer(existing_product, context={'store': store})
                
                return Response({
                    'success': True,
                    'supported': True,
                    'product': serializer.data,
                    'source': 'matched_existing',
                    'message': f'Barcode linked to existing product'
                })
            else:
                # No match found - DO NOT CREATE, just return not supported
                print(f"❌ No matching product found for: {product_name}")
                
                return Response({
                    'success': True,
                    'supported': False,
                    'message': f'Product "{product_name}" not in our database yet',
                    'barcode': barcode
                }, status=status.HTTP_200_OK)
        else:
            # Step 5: Not found in Open Food Facts either
            print(f"❌ Barcode {barcode} not found in Open Food Facts")
            
            return Response({
                'success': True,
                'supported': False,
                'message': 'Item pricing not supported at this time',
                'barcode': barcode
            }, status=status.HTTP_200_OK)