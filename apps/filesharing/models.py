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
