from rest_framework import serializers

from apps.filesharing.models import Notifications, UserFiles

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

class FileViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFiles
        
        exclude = ('UserID','FileKey',)

class NotificationSerializer(serializers.ModelSerializer):
    File = serializers.SerializerMethodField()
    Requester = serializers.SerializerMethodField()
    class Meta:
        model = Notifications
        fields = ['id','File', 'Requester'] 
    def get_File(self,obj):
        return obj.File.FileName
    def get_Requester(self,obj):
        return obj.Requester.name
    
