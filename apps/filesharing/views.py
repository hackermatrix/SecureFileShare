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
from .models import Notifications, PermTable, SharedFile, UserFiles
from authentication.models import User
from .serializers import FetchEmailSerializer, FileUploadSerializer, FileViewSerializer, NotificationSerializer, SharedFileNamesSerializer, SharedFileUserSerializer
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
            file_category = serializer.validated_data['category']
            aws.s3_client.upload_fileobj(uploaded_file, settings.AWS_STORAGE_BUCKET_NAME, s3_key)
            user_file = UserFiles(
                UserID=request.user,
                FileName=uploaded_file.name,
                FileKey=s3_key,
                FileSize=uploaded_file.size,
                FileType=uploaded_file.content_type,
                FileCategory= file_category
            )
            user_file.save()

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
        
class FetchEmailList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,format=None):
        user_id = request.user.id
        try:
          users = User.objects.all().exclude(id=user_id).exclude(is_admin=True)
          print(users)
          serialized = FetchEmailSerializer(users,many=True)
          email_list = serialized.data
          return Response({"emails":email_list})

        except Exception as e:
            return Response({"error":e})
        
class FileShare(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):

        file_id = request.data['fileid']
        email_list = request.data['emails']
        expiry_time = request.data['expiry']
        
        if file_id and email_list is not None:
            try:
                file_id = int(file_id)
                user = request.user
                
                shared_with = User.objects.filter(email__in=email_list)
                print(shared_with)

                file = UserFiles.objects.get(UserID=user.id,FileID=file_id)

                shared_file = SharedFile(
                    File = file,
                    Owner = user,
                    Expiration_time = int(expiry_time),

                )
                shared_file.FileUrl = shared_file.get_signed_url()
                shared_file.save()
                for user in shared_with:
                    shared_file.Shared_with.add(user)
                shared_file.save()

                return Response({"msg":"File Shared"},status=status.HTTP_200_OK) 
            
            except UserFiles.DoesNotExist:
                return Response({"error":"File Not Found"},status=status.HTTP_404_NOT_FOUND)
            except ClientError as e:
                return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({"error": "Invalid 'FileID' parameter."}, status=status.HTTP_400_BAD_REQUEST)


        else:
          return Response({"error":"Missing parameters"},status=status.HTTP_400_BAD_REQUEST)
        

    #Returns the list of users sharing file to the current  
class SharedFileUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user

        shared_files = SharedFile.objects.filter(Shared_with=user)


        serialized = SharedFileUserSerializer(shared_files, many=True)


        data = serialized.data


        users = set()
        for user in data:
            users.add(user["Email"])


        new =[]
        for each in users:
            new.append({'Email':each})

        return Response({"sharing_users": new})



class SharedFileNames(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,format=None):
        user = request.user
        owner_email = request.data['owner_email']
        try:
            Owner = User.objects.get(email=owner_email)
            data = SharedFile.objects.filter(Shared_with=user,Owner=Owner)
            serialized = SharedFileNamesSerializer(data,many=True)
            print(serialized.data)
            return Response({"shared_files":serialized.data})
        except Exception as e:
            return Response({"error":e})
    