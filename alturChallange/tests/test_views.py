from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from alturChallange.alturChallange.models import Call


class CallApiTests(TestCase):

    def test_upload_call(self):
        audio = SimpleUploadedFile(
            "test.wav",
            b"fake-audio-content",
            content_type="audio/wav"
        )

        response = self.client.post(
            reverse("upload_list"),
            {"audio_file": audio},
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(Call.objects.count(), 1)

    def test_call_detail(self):
        call = Call.objects.create(
            filename="demo.wav",
            status="COMPLETED",
            transcript=[],
            summary="summary",
            tags={"intent": "other"},
        )

        response = self.client.get(
            reverse("api_call_detail", args=[call.id])
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["summary"], "summary")