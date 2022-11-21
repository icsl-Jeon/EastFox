import datetime
from ..models import Timeline, Screener, Segment, ScreenerApplication
from fetch.models import Asset

from ..serializers import *

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
import sys

sys.path.append('../../')  # TODO: valid only when we start server at backend folder


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_timeline(request):
    def parse_request(reqeust_input) -> Timeline:
        from_date = reqeust_input.POST.get('from_date')
        to_date = reqeust_input.POST.get('to_date')
        name = reqeust_input.POST.get('name')
        x1 = reqeust_input.POST.get('x1')
        y1 = reqeust_input.POST.get('y1')
        x2 = reqeust_input.POST.get('x2')
        y2 = reqeust_input.POST.get('y2')

        return Timeline(user=reqeust_input.user,
                        from_date=from_date, to_date=to_date,
                        name=name,
                        x1=x1, y1=y1, x2=x2, y2=y2)

    timeline = parse_request(request)
    timeline.save()
    return Response(TimelineSerializer(timeline).data)


@api_view(['POST'])
def create_screener(request):
    def parse_request(reqeust_input) -> Screener:
        x1 = reqeust_input.POST.get('x1')
        y1 = reqeust_input.POST.get('y1')
        x2 = reqeust_input.POST.get('x2')
        y2 = reqeust_input.POST.get('y2')
        return Screener(user=reqeust_input.user, x1=x1, y1=y1, x2=x2, y2=y2)

    screener = parse_request(request)
    screener.save()
    return Response(ScreenerSerializer(screener).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_screener_application(request):
    applied_screener = Screener.objects.get(id=request.POST.get('screener_id'))
    timeline = Timeline.objects.get(id=request.POST.get('timeline_id'))
    applied_date = request.POST.get('applied_date')
    x1 = request.POST.get('x1')
    y1 = request.POST.get('y1')
    x2 = request.POST.get('x2')
    y2 = request.POST.get('y2')

    if datetime.datetime.strptime(applied_date,
                                  '%Y-%m-%d').date() >= timeline.to_date or \
            datetime.datetime.strptime(applied_date, '%Y-%m-%d').date() <= timeline.from_date:
        raise Exception(f'Screener applied date {applied_date} not included in timeline horizon.')
    old_application_exist = ScreenerApplication.objects.filter(user=request.user, timeline=timeline,
                                                               applied_date=applied_date).exists()
    if old_application_exist:
        old_application = ScreenerApplication.objects.get(user=request.user, timeline=timeline,
                                                          applied_date=applied_date)
        old_application.delete()

    application = ScreenerApplication(user=request.user, timeline=timeline, screener=applied_screener,
                                      applied_date=applied_date, x1=x1, y1=y1, x2=x2, y2=y2)
    application.save()
    return Response(ScreenerApplicationSerializer(application).data)
