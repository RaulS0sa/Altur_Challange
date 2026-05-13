import uuid

from django.db import models


class CallStatus(models.TextChoices):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Call(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    filename = models.CharField(max_length=255)

    audio_file = models.FileField(upload_to="calls/")

    status = models.CharField(
        max_length=20,
        choices=CallStatus.choices,
        default=CallStatus.PENDING,
    )

    transcript = models.TextField(blank=True)

    summary = models.TextField(blank=True)

    tags = models.JSONField(default=list)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    processed_at = models.DateTimeField(null=True, blank=True)

    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.filename} ({self.status})"