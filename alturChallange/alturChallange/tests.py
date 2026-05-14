import uuid
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Call, CallStatus

class CallSystemTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_upload_flow(self):
        """Test that uploading a file creates a DB record and returns 302."""
        audio = SimpleUploadedFile("test_call.mp3", b"fake-audio-content", content_type="audio/mpeg")
        response = self.client.post('/', {'audio_file': audio})
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Call.objects.count(), 1)
        
        call = Call.objects.first()
        self.assertEqual(call.status, CallStatus.PENDING)
        self.assertEqual(call.filename, "test_call.mp3")

    def test_api_list_view(self):
        """Test that the API returns the correct list of calls."""
        Call.objects.create(filename="call1.mp3", status=CallStatus.COMPLETED)
        response = self.client.get('/api/calls/')
        data = response.json()
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['status'], "COMPLETED")

    def test_export_endpoint(self):
        """Ensure the export JSON functionality works and has correct headers."""
        call_id = uuid.uuid4()
        Call.objects.create(id=call_id, filename="export.mp3", status=CallStatus.COMPLETED, tags={"intent": "support"})
        
        response = self.client.get(f'/api/calls/{call_id}/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], f'attachment; filename="call_{call_id}.json"')
        self.assertEqual(response.json()['tags']['intent'], "support")