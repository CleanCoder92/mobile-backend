from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

from cubes.models import Cube
from tiles.models import Tile


def cube_view(request, pk):
    try:
        cube = Cube.objects.get(id=pk)
        tiles = Tile.objects.filter(cube=cube)
        return render(request, 'index.html', context={"tiles": tiles})
    except ObjectDoesNotExist:
        return JsonResponse(data=None, status=500)


class url_view(GenericAPIView):
    def get(self, request, pk):
        cube = Cube.objects.get(id=pk)
        tiles = Tile.objects.filter(cube=cube)
        tiles_list = []
        if tiles:
            for tile in tiles:
                tiles_list.append({
                    'sequence': tile.sequence,
                    'url': tile.photo_url,
                    'link': tile.link
                })

        return Response(
            {
                "result": True,
                "data": {
                    "type": cube.type,
                    "urls": tiles_list
                }
            },
            status=status.HTTP_201_CREATED
        )
