import datetime
from .models import Strategist, Filter
from .serializers import StrategistSerializer, FilterSerializer

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
import sys

sys.path.append('../')  # TODO: valid only when we start server at backend folder

STRATEGIST = "strategist"


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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_strategist_list(request):
    return Response(StrategistSerializer(Strategist.objects.filter(user=request.user), many=True).data)


# TODO: modified to POST method
@api_view(['GET'])
def create_filter(request):
    def parse_request(reqeust_input) -> Filter:
        applied_date = reqeust_input.GET.get('applied_date')
        return Filter(user=reqeust_input.user, applied_date=applied_date)

    strategy_filter = parse_request(request)
    strategy_filter.save()
    return Response(FilterSerializer(strategy_filter).data)
