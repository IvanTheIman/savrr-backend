from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.models import GroceryList, GroceryItem, Product, Store
from api.serializers.gorcery_list_serializer import GroceryListSerializer, GroceryItemSerializer, StoreSerializer


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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def store_list(request):
    stores = Store.objects.all()
    return Response(StoreSerializer(stores, many=True).data)