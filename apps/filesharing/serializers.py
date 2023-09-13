from rest_framework import serializers

from apps.filesharing.models import UserFiles

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

class FileViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFiles
        
        exclude = ('UserID','FileKey',)
