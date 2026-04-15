# api/views/product_views.py

import requests
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import Product, Store, PriceHistory
from ..serializers.product_serializer import (
    ProductSerializer, 
    BarcodeLookupSerializer, 
    StoreSerializer,
)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    @action(detail=False, methods=['get'], url_path='barcode/(?P<barcode>[^/.]+)')
    def lookup_barcode(self, request, barcode=None):
        """
        Lookup product by barcode with Open Food Facts fallback
        GET /api/products/barcode/{barcode}/?store_id=1
        """
        store_id = request.query_params.get('store_id')
        store = None
        
        if store_id:
            try:
                store = Store.objects.get(id=store_id)
            except Store.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Store not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Step 1: Check if product exists in our database
        try:
            product = Product.objects.get(barcode=barcode)
            serializer = BarcodeLookupSerializer(product, context={'store': store})
            
            return Response({
                'success': True,
                'supported': True,
                'product': serializer.data,
                'source': 'database'
            })
            
        except Product.DoesNotExist:
            # Step 2: Product not in database, try Open Food Facts
            print(f"Product with barcode {barcode} not found. Checking Open Food Facts...")
            
            external_data = self._fetch_from_open_food_facts(barcode)
            
            if external_data:
                # Step 3: Save the product to database
                try:
                    product = Product.objects.create(
                        product_id=barcode,  # Use barcode as product_id
                        name=external_data['name'],
                        unit=external_data.get('unit', 'each'),
                        barcode=barcode,
                    )
                    
                    print(f"Successfully saved new product: {product.name}")
                    
                    # Return the newly created product
                    serializer = BarcodeLookupSerializer(product, context={'store': store})
                    
                    return Response({
                        'success': True,
                        'supported': True,
                        'product': serializer.data,
                        'source': 'open_food_facts',
                        'message': 'Product found and added to database. Price not available yet.'
                    })
                    
                except Exception as e:
                    print(f"Error saving product: {e}")
                    return Response({
                        'success': False,
                        'error': f'Failed to save product: {str(e)}'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                # Step 4: Not found anywhere
                return Response({
                    'success': True,
                    'supported': False,
                    'message': 'Item pricing not supported at this time',
                    'barcode': barcode
                }, status=status.HTTP_200_OK)
    
    def _fetch_from_open_food_facts(self, barcode):
        """
        Fetch product information from Open Food Facts API
        Returns dict with product info or None if not found
        """
        try:
            url = f'https://world.openfoodfacts.org/api/v0/product/{barcode}.json'
            print(f"Fetching from Open Food Facts: {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if product was found
                if data.get('status') == 1 and data.get('product'):
                    product_data = data['product']
                    
                    # Extract product name (try multiple fields)
                    name = (
                        product_data.get('product_name') or 
                        product_data.get('product_name_en') or 
                        product_data.get('generic_name') or
                        'Unknown Product'
                    )
                    
                    # Try to determine unit
                    unit = 'each'  # default
                    quantity = product_data.get('quantity', '')
                    if quantity:
                        if 'kg' in quantity.lower():
                            unit = 'kg'
                        elif 'g' in quantity.lower():
                            unit = 'g'
                        elif 'l' in quantity.lower() or 'liter' in quantity.lower():
                            unit = 'L'
                        elif 'ml' in quantity.lower():
                            unit = 'ml'
                    
                    print(f"Found product: {name}")
                    
                    return {
                        'name': name,
                        'unit': unit,
                        'brand': product_data.get('brands'),
                        'category': product_data.get('categories'),
                        'quantity': product_data.get('quantity'),
                    }
                else:
                    print(f"Product not found in Open Food Facts (status: {data.get('status')})")
                    return None
            else:
                print(f"Open Food Facts API returned status: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("Open Food Facts API timeout")
            return None
        except Exception as e:
            print(f"Error fetching from Open Food Facts: {e}")
            return None
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search products by name
        GET /api/products/search/?q=banana&store_id=1
        """
        query = request.query_params.get('q', '')
        store_id = request.query_params.get('store_id')
        
        if not query:
            return Response({
                'success': False,
                'error': 'Query parameter "q" is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        products = Product.objects.filter(name__icontains=query)
        
        store = None
        if store_id:
            try:
                store = Store.objects.get(id=store_id)
            except Store.DoesNotExist:
                pass
        
        serializer = BarcodeLookupSerializer(
            products, 
            many=True, 
            context={'store': store}
        )
        
        return Response({
            'success': True,
            'count': len(serializer.data),
            'products': serializer.data
        })


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """
        Get nearby stores based on lat/lng
        GET /api/stores/nearby/?lat=32.3&lng=-95.3
        """
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        
        if not lat or not lng:
            return Response({
                'success': False,
                'error': 'lat and lng parameters required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        stores = Store.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        )
        
        serializer = self.get_serializer(stores, many=True)
        
        return Response({
            'success': True,
            'stores': serializer.data
        })