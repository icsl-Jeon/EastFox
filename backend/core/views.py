import datetime

from interface.models import Screener, Timeline, ScreenerApplication, Segment
from interface.serializers import *

from fetch.models import Asset

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_segment_list_for_timeline(request):
    try:
        if len(Screener.objects.filter(user=request.user)) == 0:
            Response({})
        timeline = Timeline.objects.get(id=request.data['timeline_id'])
        Segment.objects.filter(timeline=timeline).delete()
        segment = Segment.objects.create(timeline=timeline, from_date=timeline.from_date,
                                         to_date=timeline.to_date, user=request.user)
        segment.asset_list.add(*Asset.objects.all())
        segment_array = [segment]

        ordered_screener_application = ScreenerApplication.objects.filter(timeline=timeline).order_by('applied_date')
        for application in ordered_screener_application:
            if application.applied_date >= timeline.to_date or application.applied_date <= timeline.from_date:
                continue
            segment.to_date = application.applied_date
            segment = Segment.objects.create(timeline=timeline, from_date=application.applied_date,
                                             to_date=timeline.to_date, user=request.user)
            segment_array.append(segment)
        segment_list_serialized = SegmentSerializer(segment_array, many=True).data
        return Response(segment_list_serialized)
    except Exception as e:
        return Response({})
