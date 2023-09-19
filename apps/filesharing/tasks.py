from filesec.celery import shared_task
from django.utils import timezone
from apps.filesharing.models import PermTable

@shared_task
def delete_expired_permissions():
    current_time = timezone.now()
    expired_permissions = PermTable.objects.filter(is_approved=True)

    for permission in expired_permissions:
        start_time = permission.Last_Modified
        expire_minutes = permission.Expiry_Time  # Expiry_Time in minutes
        expiration_time = start_time + timezone.timedelta(minutes=expire_minutes)

        if current_time >= expiration_time:
            permission.delete()
