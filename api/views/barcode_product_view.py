# api/views/barcode_product_view.py

import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from ..models import Product, Store, ProductBarcode
from ..serializers.product_serializer import BarcodeLookupSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def barcode_lookup_view(request, barcode):
    """
    Lookup product by barcode - saves new barcodes automatically
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
            }, status=status.HTTP_404_NOT_FOUND)
    
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
        # Step 2: Barcode not found - try Open Food Facts
        print(f"Barcode {barcode} not found in database. Checking Open Food Facts...")
        
        external_data = fetch_from_open_food_facts(barcode)
        
        if external_data:
            # Step 3: Found in Open Food Facts - try to match or create product
            product_name = external_data['name']
            
            # Try to find existing product with similar name
            existing_product = Product.objects.filter(
                Q(name__iexact=product_name) |  # Exact match (case insensitive)
                Q(name__icontains=product_name.split()[0])  # First word match
            ).first()
            
            if existing_product:
                # Match found - link barcode to existing product
                print(f"Matched barcode {barcode} to existing product: {existing_product.name}")
                
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
                    'message': f'Barcode linked to existing product: {existing_product.name}'
                })
            else:
                # No match - create new product
                print(f"Creating new product for barcode {barcode}: {product_name}")
                
                new_product = Product.objects.create(
                    product_id=f"auto_{barcode}",
                    name=product_name,
                    unit=external_data.get('unit', 'each'),
                )
                
                ProductBarcode.objects.create(
                    product=new_product,
                    barcode=barcode,
                    variant_name=product_name,
                    source='Open Food Facts'
                )
                
                serializer = BarcodeLookupSerializer(new_product, context={'store': store})
                
                return Response({
                    'success': True,
                    'supported': True,
                    'product': serializer.data,
                    'source': 'created_new',
                    'message': 'New product created from Open Food Facts. Price not available yet.'
                })
        else:
            # Step 4: Not found anywhere
            print(f"Barcode {barcode} not found in Open Food Facts")
            
            return Response({
                'success': True,
                'supported': False,
                'message': 'Item pricing not supported at this time',
                'barcode': barcode
            }, status=status.HTTP_200_OK)


def fetch_from_open_food_facts(barcode):
    """
    Fetch product information from Open Food Facts API
    Returns dict with product info or None if not found
    """
    try:
        url = f'https://world.openfoodfacts.net/api/v2/product/{barcode}'
        print(f"Fetching from Open Food Facts: {url}")
        
        headers = {
            'User-Agent': 'GroceryPriceApp/1.0',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 1 and data.get('product'):
                product_data = data['product']
                
                # Extract product name
                name = (
                    product_data.get('product_name') or 
                    product_data.get('product_name_en') or 
                    product_data.get('generic_name') or
                    'Unknown Product'
                )
                
                # Try to determine unit
                unit = 'each'
                quantity = product_data.get('quantity', '')
                if quantity:
                    quantity_lower = quantity.lower()
                    if 'kg' in quantity_lower:
                        unit = 'kg'
                    elif 'g' in quantity_lower and 'kg' not in quantity_lower:
                        unit = 'g'
                    elif 'l' in quantity_lower or 'liter' in quantity_lower:
                        unit = 'L'
                    elif 'ml' in quantity_lower:
                        unit = 'ml'
                
                print(f"✅ Found product: {name}")
                
                return {
                    'name': name,
                    'unit': unit,
                }
            else:
                print(f" Product not found in Open Food Facts")
                return None
        elif response.status_code == 404:
            print(f" Product {barcode} not found in Open Food Facts database")
            return None
        else:
            print(f" Open Food Facts API returned status: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("⏱️ Open Food Facts API timeout")
        return None
    except Exception as e:
        print(f" Error fetching from Open Food Facts: {e}")
        return None
    
@api_view(['POST'])
def add_barcode_to_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        barcode = request.data.get('barcode')
        
        if not barcode:
            return Response({'error': 'Barcode required'}, status=400)
        
        # Save or update barcode
        product.barcode = barcode
        product.save()
        
        return Response({
            'success': True,
            'message': 'Barcode added to product'
        })
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)