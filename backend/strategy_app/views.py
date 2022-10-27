import datetime
from .models import Strategist, Filter, Segment, FilterApplication
from fetch.models import Asset

from .serializers import *

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
import sys

sys.path.append('../')  # TODO: valid only when we start server at backend folder

STRATEGIST = "strategist"


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_strategist_list(request):
    return Response(StrategistSerializer(Strategist.objects.filter(user=request.user), many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_filter_list(request):
    return Response(FilterSerializer(Filter.objects.filter(user=request.user), many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_filter_application_list(request):
    return Response(FilterApplicationSerializer(FilterApplication.objects.filter(user=request.user), many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_strategist(request):
    def parse_request(reqeust_input) -> Strategist:
        from_date = reqeust_input.POST.get('from_date')
        to_date = reqeust_input.POST.get('to_date')
        name = reqeust_input.POST.get('name')
        x1 = reqeust_input.POST.get('x1')
        y1 = reqeust_input.POST.get('y1')
        x2 = reqeust_input.POST.get('x2')
        y2 = reqeust_input.POST.get('y2')

        return Strategist(user=reqeust_input.user,
                          from_date=from_date, to_date=to_date,
                          name=name,
                          x1=x1, y1=y1, x2=x2, y2=y2)

    strategist = parse_request(request)
    strategist.save()
    return Response(StrategistSerializer(strategist).data)


@api_view(['POST'])
def create_filter(request):
    def parse_request(reqeust_input) -> Filter:
        x1 = reqeust_input.POST.get('x1')
        y1 = reqeust_input.POST.get('y1')
        x2 = reqeust_input.POST.get('x2')
        y2 = reqeust_input.POST.get('y2')
        return Filter(user=reqeust_input.user, x1=x1, y1=y1, x2=x2, y2=y2)

    strategy_filter = parse_request(request)
    strategy_filter.save()
    return Response(FilterSerializer(strategy_filter).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_filter_to_strategist(request):
    try:
        applied_filter = Filter.objects.get(id=request.POST.get('filter_id'))
        strategist = Strategist.objects.get(id=request.POST.get('strategist_id'))
        applied_date = request.POST.get('applied_date')
        x1 = request.POST.get('x1')
        y1 = request.POST.get('y1')
        x2 = request.POST.get('x2')
        y2 = request.POST.get('y2')

        if datetime.datetime.strptime(applied_date,
                                      '%Y-%m-%d').date() >= strategist.to_date or \
                datetime.datetime.strptime(applied_date, '%Y-%m-%d').date() <= strategist.from_date:
            raise Exception(f'Filter applied date {applied_date} not included in strategist horizon.')

        application = FilterApplication(strategist=strategist, filter=applied_filter,
                                        applied_date=applied_date, x1=x1, y1=y1, x2=x2, y2=y2)
        application.save()
        return Response(True)

    except Exception as e:
        return Response(False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def calculate_segment_list(request):
    try:
        strategist = Strategist.objects.get(id=request.GET.get('strategist_id'))
        Segment.objects.filter(strategist=strategist).delete()

        segment = Segment.objects.create(strategist=strategist, from_date=strategist.from_date,
                                         to_date=strategist.to_date)
        segment.asset_list.add(*Asset.objects.all())

        ordered_filter_application = FilterApplication.objects.filter(strategist=strategist).order_by('applied_date')
        for application in ordered_filter_application:
            if application.applied_date >= strategist.to_date or application.applied_date <= strategist.from_date:
                continue
            segment.to_date = application.applied_date
            segment.save()
            segment = Segment.objects.create(strategist=strategist, from_date=application.applied_date,
                                             to_date=strategist.to_date)
        segment_list_serialized = SegmentSerializer(Segment.objects.filter(strategist=strategist), many=True).data
        return Response(segment_list_serialized)
    except Exception as e:
        return Response({})
