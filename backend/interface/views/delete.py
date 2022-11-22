from ..serializers import *

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from rest_framework.response import Response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_timeline_list(request):
    try:
        timeline_id_list = request.POST.getlist('timeline_id_list')
        Timeline.objects.filter(user=request.user, pk__in=[int(id) for id in timeline_id_list]).delete()
        return Response(True)
    except Exception as e:
        return Response(False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_screener_list(request):
    try:
        screener_id_list = request.POST.getlist('screener_id_list')
        Screener.objects.filter(user=request.user, pk__in=[int(id) for id in screener_id_list]).delete()
        return Response(True)
    except Exception as e:
        return Response(False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_screener_application_list(request):
    try:
        screener_application_id_list = request.POST.getlist('screener_application_id_list')
        ScreenerApplication.objects.filter(user=request.user,
                                           pk__in=[int(id) for id in screener_application_id_list]).delete()
        return Response(True)
    except Exception as e:
        return Response(False)
