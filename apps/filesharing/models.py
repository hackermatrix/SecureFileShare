from django.db import models
from authentication.models import User
from django.utils import timezone


class UserFiles(models.Model):
    FileID = models.AutoField(primary_key=True)
    UserID = models.ForeignKey(User, on_delete=models.CASCADE)
    FileName = models.CharField(max_length=255)
    FileKey = models.CharField(max_length=255)
    FileSize = models.BigIntegerField(default=0)
    FileType = models.CharField(max_length=50)
    UploadedAt = models.DateTimeField(default=timezone.now)  
    LastModifiedAt = models.DateTimeField(default=timezone.now)
    SharedWith = models.CharField

    def __str__(self):
        return (f"{self.FileID} - {self.FileName}")
