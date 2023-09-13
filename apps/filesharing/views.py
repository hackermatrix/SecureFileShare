from django.shortcuts import render
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
from .models import UserFiles
from authentication.models import User
from .serializers import FileUploadSerializer, FileViewSerializer




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
            access_key = os.urandom(32)
            aws.s3_client.upload_fileobj(uploaded_file, settings.AWS_STORAGE_BUCKET_NAME, s3_key,ExtraArgs={'SSECustomerAlgorithm': 'AES256','SSECustomerKey': access_key})
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


