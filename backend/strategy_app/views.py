import datetime
from .models import Strategist
from .serializers import StrategistSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
import sys

sys.path.append('../')  # TODO: valid only when we start server at backend folder
from .apps import db_interface

STRATEGIST = "strategist"


@api_view(['GET'])
def connect_check(request):
    return Response("You're reaching connection check url.")


@api_view(['GET'])
def create_strategist(request):
    def parse_request(reqeust_input) -> Strategist:
        asset_pool = reqeust_input.GET.getlist("asset_pool", [])
        from_date = reqeust_input.GET.get('from_date')
        to_date = reqeust_input.GET.get('to_date')
        name = reqeust_input.GET.get('name')
        strategist = Strategist(asset_pool=asset_pool, from_date=from_date, to_date=to_date, name=name)
        return strategist

    if STRATEGIST in request.session.keys():
        Response(request.session[STRATEGIST])

    strategist = parse_request(request)
    # TODO: multiple strategist in a single session
    request.session[STRATEGIST] = StrategistSerializer(strategist, many=False).data

    return Response(request.session[STRATEGIST])


@api_view(['GET'])
def fetch_strategist_in_session(request):
    if STRATEGIST in request.session:
        return Response(request.session[STRATEGIST])

    return Response("No strategist in your session")
