from unittest.mock import patch, Mock

from django.test import TestCase

from alturChallange.alturChallange.models import Call, CallStatus
from alturChallange.alturChallange.tasks import process_call


class ProcessCallTests(TestCase):

    @patch("alturChallange.alturChallange.tasks.transcribe")
    @patch("alturChallange.alturChallange.tasks.run_analysis")
    @patch("alturChallange.alturChallange.tasks.requests.get")
    def test_process_call_success(
        self,
        mock_request_get,
        mock_analysis,
        mock_transcribe,
    ):

        # Mock requests.get response
        mock_response = Mock()
        mock_response.content = b"fake audio bytes"
        mock_response.raise_for_status.return_value = None

        mock_request_get.return_value = mock_response

        # Mock transcription
        mock_transcribe.return_value = [
            {
                "speaker": 0,
                "text": "hello"
            }
        ]

        # Mock analysis
        mock_analysis.return_value = {
            "summary": "successful call",
            "tags": {
                "intent": "support_request",
                "outcome": "completed",
                "sentiment": "positive",
            }
        }

        call = Call.objects.create(
            filename="test.wav",
            audio_file="calls/test.wav",
            status=CallStatus.PENDING,
        )

        process_call(call.id)

        call.refresh_from_db()

        self.assertEqual(
            call.status,
            CallStatus.COMPLETED
        )

        self.assertEqual(
            call.summary,
            "successful call"
        )

    @patch("alturChallange.alturChallange.tasks.transcribe")
    def test_process_call_failure(
        self,
        mock_transcribe
    ):
        mock_transcribe.side_effect = Exception(
            "Deepgram failed"
        )

        call = Call.objects.create(
            filename="test.wav",
            audio_file="calls/test.wav",
            status=CallStatus.PENDING,
        )

        try:
            process_call(call.id)
        except Exception:
            pass

        call.refresh_from_db()

        self.assertEqual(
            call.status,
            CallStatus.FAILED
        )