from authentication.models import User
from rest_framework import serializers

from apps.filesharing.models import Notifications, SharedFile, UserFiles

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    category = serializers.CharField()

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

class FetchEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']

class SharedFileUserSerializer(serializers.ModelSerializer):
    Email = serializers.SerializerMethodField()
    users = set()
    class Meta:
        model = SharedFile
        fields = ['Email']
        prefetch_related = ['Owner']
    def get_Email(self,obj):
        return obj.Owner.email
  
    
class SharedFileNamesSerializer(serializers.ModelSerializer):
    FileID = serializers.SerializerMethodField()
    FileName = serializers.SerializerMethodField()
    
    class Meta:
        model = SharedFile
        fields = ["FileID","FileName","FileUrl"]
    def get_FileID(self,obj):
        return obj.File.FileID
    def get_FileName(self,obj):
        return obj.File.FileName