from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from api.models import PriceHistory, Product, Store
from api.serializers.product_serializer import ProductSerializer
from django.db.models import Prefetch, OuterRef, Subquery, Min
from api.services.location.google_maps import distance


@api_view(['GET'])
@permission_classes([AllowAny])
def products_info(request):
    user_lat = request.query_params.get('lat')
    user_lon = request.query_params.get('lng')
    radius = float(request.query_params.get('distance', 20.0))

    print("LAT:", request.GET.get("lat"))
    print("LNG:", request.GET.get("lng"))
    print("DIST:", request.GET.get("distance"))

    stores = Store.objects.filter(
        latitude__isnull = False,
        longitude__isnull = False
    )

    store_list = list(stores)
    store_coords = [(s.latitude, s.longitude) for s in store_list]
    road_distances = distance((user_lat, user_lon), store_coords)

    closest_stores = [
        store_list[i].id
        for i, dist in enumerate(road_distances)
        if dist and dist['distance_miles'] <= radius
    ]

    if not closest_stores:
        return Response(
            {'error': f'No stores found within {radius} miles'},
            status = status.HTTP_404_NOT_FOUND
        )

    latest_prices = PriceHistory.objects.filter(
        store_id__in = closest_stores,
        product = OuterRef('product'),
        store__name = OuterRef('store__name'),
    ).values('product', 'store__name').annotate(
        min_price = Min('price')
    ).values('min_price')[:1]

    newest_prices = PriceHistory.objects.filter(
        store_id__in = closest_stores,
        price = Subquery(latest_prices)
    ).order_by(
        'product', 'store__name', 'date', 'price'
    ).distinct('product', 'store__name').select_related('store')


    queryset =  Product.objects.prefetch_related(
        Prefetch('pricehistory_set', queryset = newest_prices, to_attr = 'latest_prices')
    )

    for product in queryset:
        product.latest_prices.sort(key = lambda p: float(p.price))

    serializer = ProductSerializer(queryset, many = True)
    return Response(serializer.data)