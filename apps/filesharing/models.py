from django.db import models
from authentication.models import User
from django.utils import timezone
import datetime

from filesec import settings
from .utils.aws import cloudfront,s3_client


class UserFiles(models.Model):
    FileID = models.AutoField(primary_key=True)
    UserID = models.ForeignKey(User, on_delete=models.CASCADE)
    FileName = models.CharField(max_length=255)
    FileKey = models.CharField(max_length=255)
    FileSize = models.BigIntegerField(default=0)
    FileType = models.CharField(max_length=50)
    FileCategory = models.CharField(max_length=50,default="")
    UploadedAt = models.DateTimeField(default=timezone.now)  
    LastModifiedAt = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return (f"{self.FileID} - {self.FileName}")
    
class SharedFile(models.Model):
    File = models.ForeignKey(UserFiles, on_delete=models.CASCADE)
    Owner = models.ForeignKey(User, on_delete=models.CASCADE)
    Shared_with = models.ManyToManyField(User, related_name='shared_files')
    Expiration_time = models.BigIntegerField()
    LastModifiedAt = models.DateTimeField(default=timezone.now)
    FileUrl = models.URLField(default="")

    def get_signed_url(self):

        distribution_id = 'E29V79BB9SHF9I'
        object_key = self.File.FileKey

        signed_url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': object_key,
                "ResponseContentType": self.File.FileType
            },
            ExpiresIn=self.Expiration_time*60,
            
        )

        return signed_url

    def __str__(self):
        return self.File.FileName
    
class PermTable(models.Model):
    File = models.ForeignKey(UserFiles, on_delete=models.CASCADE)
    Requester = models.ForeignKey(User, on_delete=models.CASCADE)
    Owner_id = models.IntegerField() 
    is_approved = models.BooleanField(default=False)
    Last_Modified = models.DateTimeField(default=timezone.now)
    Expiry_Time = models.BigIntegerField(default=1000000)

    def __str__(self):
        return f"{self.Requester.id} - {self.File.FileName}"
    
class Notifications(models.Model):
    File = models.ForeignKey(UserFiles, on_delete=models.CASCADE)
    Requester = models.ForeignKey(User, on_delete=models.CASCADE)
    Owner_id = models.IntegerField() 
    PermTable = models.ForeignKey(PermTable, on_delete=models.CASCADE, related_name='notifications',default=None)

    def __str__(self):
        return f"{self.Requester.id} - {self.File.FileName}"
