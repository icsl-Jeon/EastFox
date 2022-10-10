from rest_framework.decorators import api_view
from rest_framework.response import Response
from .tasks import get_all_symbols_from_source, get_symbol_detail_from_source
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from core.constants import SectorEnum
from .models import Sector, Asset
from .serializers import SectorSerializer


@api_view(['POST'])
@permission_classes([IsAdminUser])
def prepare(request):
    [Sector(name=sector).save() for sector in SectorEnum]
    return Response(SectorSerializer(Sector.objects.all(), many=True).data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def update(request):
    symbols = get_all_symbols_from_source()
    for symbol in symbols:
        detail = get_symbol_detail_from_source(symbol)
        if len(detail) == 0:
            continue

    return Response("update requested.")
