from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.models import GroceryList, GroceryItem, Product
from api.serializers.grocery_serializer import GroceryListSerializer, GroceryItemSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def grocery_lists(request):
    if request.method == 'GET':
        lists = GroceryList.objects.filter(owner=request.user).prefetch_related('items__product')
        serializer = GroceryListSerializer(lists, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = GroceryListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def grocery_list_detail(request, list_id):
    try:
        grocery_list = GroceryList.objects.get(id=list_id, owner=request.user)
    except GroceryList.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    grocery_list.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_item(request, list_id):
    try:
        grocery_list = GroceryList.objects.get(id=list_id, owner=request.user)
    except GroceryList.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # accepts product name as free text, matches or creates product
    name = request.data.get('name', '').strip()
    if not name:
        return Response({'error': 'name is required'}, status=status.HTTP_400_BAD_REQUEST)

    product, _ = Product.objects.get_or_create(
        name__iexact=name,
        defaults={'name': name, 'product_id': name.lower().replace(' ', '_'), 'unit': ''}
    )

    item, created = GroceryItem.objects.get_or_create(
        grocery_list=grocery_list,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        item.quantity += 1
        item.save()

    return Response(GroceryItemSerializer(item).data, status=status.HTTP_201_CREATED)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def item_detail(request, list_id, item_id):
    try:
        item = GroceryItem.objects.get(
            id=item_id,
            grocery_list__id=list_id,
            grocery_list__owner=request.user
        )
    except GroceryItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        serializer = GroceryItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)