from django.shortcuts import render
from django.http import HttpResponse
import sys

sys.path.append('../')  # TODO: valid only when we start server at backend folder

from core.strategy import Strategist

STRATEGIST = 'strategist'


def connect_check(request):
    return HttpResponse("You're reaching connection check url.")


def create_strategist(request):
    request.session[STRATEGIST] = True
    return HttpResponse("Strategist was created!")


def apply_filter_to_strategist(request):
    if not request.session.get(STRATEGIST, None):
        return HttpResponse("Your session does not have strategist yet.")
    else:
        return HttpResponse(f"Your session has strategist! value = {request.session.get(STRATEGIST, None)}")
