from django.urls import path
from . import views
# from rest_framework_simplejwt import view
urlpatterns = [

    path("upload",views.FileUpload.as_view(),name="Url test"),
    path("listing",views.FileView.as_view(),name="List Files"),
    path("file/delete",views.FileDelete.as_view(),name="Delete Files"),
    path("file/download",views.FileDownload.as_view(),name="Download a File"),
    path("get/emails",views.FetchEmailList.as_view(),name="send Email List"),
    path("share/email-list",views.FileShare.as_view(),name="Receive Selected emails"),
    path("get/shared-file-user",views.SharedFileUser.as_view(),name="Get the username of the owner"),
    path("get/shared-files",views.SharedFileNames.as_view(),name="Get files  shared ")
    
    # path("file/share/link",views.FileLink.as_view(),name="Get File Share Link"),
    # path("file/request",views.RequestHandler.as_view(),name="Get File perms"),
    # path("file/approve",views.ApproveRequestHandler.as_view(),name="Approval request Handler"),
    # path("get/notify",views.NotificationRequestHandler.as_view(),name="Notification request Handler"),
    # path("get/action",views.AccessHandler.as_view(),name="Approval Handler")


]