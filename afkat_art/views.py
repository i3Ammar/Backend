from rest_framework import  generics

from afkat_art.models import ArtModel,TagsModel


# Create your views here.




class ArtView(generics.RetrieveUpdateAPIView,):
   queryset = ArtModel.objects.all().select_related('tags')
