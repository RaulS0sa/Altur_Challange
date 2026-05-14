from celery import shared_task
from django.utils import timezone
from time import sleep

from .models import Call, CallStatus
import os

import json
from .services.stt_service import transcribe

#from .services.analysis_service import run_analysis
from .services.analysis_service_groq import run_analysis

import requests
from tempfile import NamedTemporaryFile



@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_call(self, call_id):
    call = Call.objects.get(id=call_id)

    try:
        if call.status == CallStatus.COMPLETED:
            return
        if call.status == CallStatus.PROCESSING:
            return
        call.status = CallStatus.PROCESSING
        call.save()

        start = timezone.now()


        print(f"Processing: {call.audio_file.path}")
        # transcript = transcribe(call.audio_file.path)
        url = call.audio_file.url
        response = requests.get(url)
        response.raise_for_status()

        with NamedTemporaryFile(suffix=".wav") as tmp:
            tmp.write(response.content)
            tmp.flush()

            transcript = transcribe(tmp.name)


        call.transcript = transcript
        conv = json.dumps(transcript)
        analysis_json = run_analysis(conv)

        call.summary = analysis_json.get("summary", "summary not available")

        call.tags = analysis_json.get("tags", {})

        call.processed_at = timezone.now()

        call.status = CallStatus.COMPLETED

        end = timezone.now()

        call.processing_seconds = (
            end - start
        ).total_seconds()

        call.save()

    except Exception as ex:
        call.status = CallStatus.FAILED
        call.error_message = str(ex)
        call.save()

        print(f"Task failed for call {call_id}: {ex}. Retrying...")
        raise self.retry(exc=ex, countdown=30)
    
