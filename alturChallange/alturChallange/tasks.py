from celery import shared_task
from django.utils import timezone
from time import sleep

from .models import Call, CallStatus


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_call(self, call_id):
    call = Call.objects.get(id=call_id)

    try:
        call.status = CallStatus.PROCESSING
        call.save()

        print(f"Processing: {call.audio_file.path}")

        sleep(10)

        call.transcript = (
            f"Fake transcript for {call.filename}"
        )

        call.summary = (
            "Fake AI-generated summary"
        )

        call.tags = [
            "sales",
            "demo",
        ]

        call.processed_at = timezone.now()

        call.status = CallStatus.COMPLETED

        call.save()

    except Exception as ex:
        call.status = CallStatus.FAILED
        call.error_message = str(ex)
        call.save()

        print(f"Task failed for call {call_id}: {ex}. Retrying...")
        raise self.retry(exc=ex, countdown=30)