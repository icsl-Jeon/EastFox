from rest_framework.decorators import api_view
from rest_framework.response import Response
from .tasks import update_subroutine


@api_view(['POST'])
def update(request):
    update_subroutine(0, repeat=1)
    update_subroutine(1, repeat=1)
    print("Update requested.")
    return Response("update requested.")
