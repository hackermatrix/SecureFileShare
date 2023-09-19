from base64 import b64decode, b64encode
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.http.response import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import boto3
from rest_framework.parsers import FileUploadParser
from botocore.exceptions import NoCredentialsError, ClientError
from rest_framework import status 
from filesec import settings
from .utils import aws
from .models import Notifications, PermTable, UserFiles
from authentication.models import User
from .serializers import FileUploadSerializer, FileViewSerializer, NotificationSerializer
import json



# class FileUpload(APIView):
#     parser_classes = [FileUploadParser]

#     def put(self,request,filename, format=None):
#         file_obj = request.data['files']
#         return Res

import os

class FileUpload(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)

        if serializer.is_valid():
            user_id = request.user.id
            uploaded_file = serializer.validated_data['file']
            s3_key = f'user_{user_id}/{uploaded_file.name}'
            # access_key = os.urandom(32)
            aws.s3_client.upload_fileobj(uploaded_file, settings.AWS_STORAGE_BUCKET_NAME, s3_key)
            user_file = UserFiles(
                UserID=request.user,
                FileName=uploaded_file.name,
                FileKey=s3_key,
                FileSize=uploaded_file.size,
                FileType=uploaded_file.content_type,
            )
            user_file.save()
            print(uploaded_file.size)

            return Response({"msg":"Upload Success!!"},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# This View Class handles the File listings on S3 Buckets        
class FileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,format=None):
        try:
            user_data = UserFiles.objects.filter(UserID=request.user.id)
            serializer = FileViewSerializer(user_data,many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error":e},status=status.HTTP_400_BAD_REQUEST)
        


# Deleting Files from database as well as S3        
class FileDelete(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # Get the 'fileid' query parameter and convert it to an integer
        fileid = request.query_params.get('fileid')
        if fileid is not None:
            try:
                fileid = int(fileid)
                file_delete = UserFiles.objects.get(UserID=request.user.id, FileID=fileid)
                response = aws.s3_client.delete_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=file_delete.FileKey
                )

                
                file_delete.delete()
                return Response({"msg": "Deleted!"}, status=status.HTTP_200_OK)

                
            except UserFiles.DoesNotExist:
                return Response({"error": "File not found."}, status=status.HTTP_404_NOT_FOUND)
            except ClientError as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except ValueError:
                return Response({"error": "Invalid 'fileid' parameter."}, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response({"error": "Missing 'fileid' parameter."}, status=status.HTTP_400_BAD_REQUEST)



class FileDownload(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):

        file_id = request.query_params.get('fileid')
        if file_id is not None:
            try:
                file_id = int(file_id)
                user_id = request.user.id
                file_to_download = UserFiles.objects.get(FileID=file_id,UserID=user_id)
                file_name = file_to_download.FileName
                file_key = file_to_download.FileKey
                # # access_key = file_to_download.AccessKey

                res = aws.s3_client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                               Key=file_key)
                
                # print(res)
                response = HttpResponse(content=res['Body'],content_type='application/octet-stream')

                response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                return response 
            
            except UserFiles.DoesNotExist:
                return Response({"error":"File Not Found"},status=status.HTTP_404_NOT_FOUND)
            except ClientError as e:
                return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({"error": "Invalid 'FileID' parameter."}, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response({"error":"Missing 'FileID' parameter"},status=status.HTTP_400_BAD_REQUEST)
        

class FileLink(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):

        file_id = request.query_params.get('fileid')
        if file_id is not None:
            try:
                file_id = int(file_id)
                user_id = request.user.id
                share_token = b64encode(json.dumps({"userid":user_id,"fileid":file_id}).encode('utf-8'))
                return Response({"token":share_token}) 
            
            except UserFiles.DoesNotExist:
                return Response({"error":"File Not Found"},status=status.HTTP_404_NOT_FOUND)
            except ClientError as e:
                return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({"error": "Invalid 'FileID' parameter."}, status=status.HTTP_400_BAD_REQUEST)


        else:
          return Response({"error":"Missing 'FileID' parameter"},status=status.HTTP_400_BAD_REQUEST)


class RequestHandler(APIView):
    permission_classes = [IsAuthenticated]

    def download_file(self,user_id,file_id):
        file_to_download = UserFiles.objects.get(FileID=file_id,UserID=user_id)
        file_name = file_to_download.FileName
        file_key = file_to_download.FileKey

        res = aws.s3_client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                                        Key=file_key)
        file_type = file_to_download.FileType
         # print(res)
        response = HttpResponse(content=res['Body'],content_type=file_type,status=status.HTTP_200_OK)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'

        return response 


    def get(self, request, format=None):
        token = request.query_params.get('token')  # Extract the token from the request data

        if token is not None:
            try:
                # Decode the token to obtain data about the file share request
                data = json.loads(b64decode(token))
                user_id = data['userid']
                file_id = data['fileid']

                # Retrieve the file associated with the request (based on data['file_id'])
                file = get_object_or_404(UserFiles, FileID=file_id,UserID=user_id)

                
                # Check if a FileShareRequest entry already exists for this file and requester
                existing_request = PermTable.objects.filter(
                    File=file,
                    Requester=request.user,
                ).first()
                
                if(user_id!=request.user.id):
                    if (existing_request and existing_request.is_approved==False):
                        return Response({"msg": "You dont have Permission to Access this file"},
                                        status=status.HTTP_403_FORBIDDEN)
                    elif(existing_request and existing_request.is_approved==True):
                        

                        #Downloading the file
                        return self.download_file(user_id,file_id)

                    else:
                        # Create a file share request entry without specifying the permission level
                        file_share_request = PermTable(
                            File=file,
                            Requester=request.user,
                            Owner_id = file.UserID.id,
                            is_approved = False
                        )
                        file_share_request.save()

                        return Response({"msg": "You dont have Permission to Access this file"},
                                        status=status.HTTP_200_OK)
                else:
                    return self.download_file(user_id,file_id)

            except UserFiles.DoesNotExist:
                return Response({"error": "File not found."}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Missing 'token' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        
class ApproveRequestHandler(APIView):
    permission_classes = [IsAuthenticated]

    def send_notification(self,File,Requester,Owner_id):
        perm_table_instance = PermTable.objects.get(File=File,Requester=Requester,Owner_id=Owner_id) 
        notify = Notifications(
            Owner_id = Owner_id,
            Requester = Requester,
            File = File,
            PermTable = perm_table_instance
        )         
        notify.save()


    def get(self, request, format=None):
        token = request.query_params.get('token')
        
        if token is not None:
            try:
                data = json.loads(b64decode(token).decode('utf-8'))
                owner_id = data.get('userid')

                # Query for pending approval requests for the owner
                pending_requests = PermTable.objects.filter(Owner_id=owner_id, is_approved=False)

               
                for request in pending_requests:
                    # Check if a notification already exists for this request
                    existing_notification = Notifications.objects.filter(File=request.File, Requester=request.Requester).first()
                    if not existing_notification:
                        self.send_notification(request.File,request.Requester,request.Owner_id)

                return Response({"msg": "Approval requests sent successfully."},
                                status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Missing 'token' parameter"}, status=status.HTTP_400_BAD_REQUEST)


class NotificationRequestHandler(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,format=None):
        try:
            notification_list = Notifications.objects.filter(Owner_id = request.user.id)
            serialize = NotificationSerializer(notification_list,many=True)
            
            return Response(serialize.data,status=status.HTTP_200_OK)
        except Exception as e:
            return  Response({"error":e},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AccessHandler(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            action = request.data.get('action') 
            notification_id = request.data.get('notification_id')
            expiry_time = request.data.get('expiry_time')

            notification = Notifications.objects.get(id=notification_id)

            if action == 'allow':

                perm_request = notification.PermTable  # Get the related PermTable entry
                perm_request.is_approved = True  # Grant access
                perm_request.Last_Modified = timezone.now()
                perm_request.Expiry_Time = expiry_time
                perm_request.save()

            elif action == 'deny':

                perm_request = notification.PermTable 
                perm_request.delete()  

            # Delete the notification entry
            notification.delete()


            return Response({"msg": f"{action.capitalize()} request processed successfully."},
                            status=status.HTTP_200_OK)

        except Notifications.DoesNotExist:
            return Response({"error": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)