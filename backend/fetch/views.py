import background_task.tasks
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from core.constants import SectorEnum, AssetTypeEnum, ExchangeEnum
from .models import Sector, Exchange, AssetType

from .tasks import update_asset_database
from background_task.tasks import Task


@api_view(['POST'])
@permission_classes([IsAdminUser])
def prepare(request):
    [Sector(sector).save() for sector in SectorEnum]
    [AssetType(asset_type).save() for asset_type in AssetTypeEnum]
    [Exchange(exchange).save() for exchange in ExchangeEnum]

    return Response(f"Prepared: {len(Sector.objects.all())} sectors"
                    f" and {len(AssetType.objects.all())} asset types"
                    f" and {len(Exchange.objects.all())} exchanges")


@api_view(['POST'])
@permission_classes([IsAdminUser])
def update(request):
    # TODO: add repeat argument
    update_asset_database()
    return Response("update requested.")
