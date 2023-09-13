from django.urls import path
from . import views
# from rest_framework_simplejwt import view
urlpatterns = [

    path("upload",views.FileUpload.as_view(),name="Url test"),
    path("listing",views.FileView.as_view(),name="List Files"),
    path("file/delete",views.FileDelete.as_view(),name="Delete Files"),


]