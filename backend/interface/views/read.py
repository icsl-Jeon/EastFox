import datetime
from ..models import Timeline, Screener, Segment, ScreenerApplication
from fetch.models import Asset

from ..serializers import *

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
import sys

sys.path.append('../../')  # TODO: valid only when we start server at backend folder


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def read_timeline_list(request):
    return Response(TimelineSerializer(Timeline.objects.filter(user=request.user), many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def read_screener_list(request):
    return Response(ScreenerSerializer(Screener.objects.filter(user=request.user), many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def read_screener_application_list(request):
    return Response(
        ScreenerApplicationSerializer(ScreenerApplication.objects.filter(user=request.user), many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def read_segment_list(request):
    return Response(SegmentSerializer(Segment.objects.filter(user=request.user), many=True).data)
