import json

from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from .models import Call
from .tasks import process_call


def upload_list(request):
    if request.method == "POST":
        audio = request.FILES.get("audio_file")
        if not audio:
            return HttpResponseBadRequest("Missing audio_file.")

        call = Call.objects.create(filename=audio.name, audio_file=audio)
        process_call.delay(str(call.id))
        return redirect("upload_list")

    calls = Call.objects.order_by("-uploaded_at")
    return render(request, "upload.html", {"calls": calls})


def api_calls(request):
    if request.method == "GET":
        calls = Call.objects.order_by("-uploaded_at")
        data = [
            {
                "id": str(call.id),
                "filename": call.filename,
                "status": call.status,
                "uploaded_at": call.uploaded_at.isoformat(),
                "processed_at": call.processed_at.isoformat() if call.processed_at else None,
                "audio_url": request.build_absolute_uri(call.audio_file.url) if call.audio_file else None,
            }
            for call in calls
        ]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        audio = request.FILES.get("audio_file")
        if not audio:
            return JsonResponse({"error": "Missing audio_file."}, status=400)

        call = Call.objects.create(filename=audio.name, audio_file=audio)
        process_call.delay(str(call.id))
        response_data = {
            "id": str(call.id),
            "filename": call.filename,
            "status": call.status,
            "uploaded_at": call.uploaded_at.isoformat(),
            "audio_url": request.build_absolute_uri(call.audio_file.url) if call.audio_file else None,
        }
        return JsonResponse(response_data, status=201)

    return JsonResponse({"error": "Method not allowed."}, status=405)


def api_call_detail(request, call_id):
    call = get_object_or_404(Call, id=call_id)
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed."}, status=405)

    response_data = {
        "id": str(call.id),
        "filename": call.filename,
        "status": call.status,
        "uploaded_at": call.uploaded_at.isoformat(),
        "processed_at": call.processed_at.isoformat() if call.processed_at else None,
        "transcript": call.transcript,
        "summary": call.summary,
        "tags": call.tags,
        "audio_url": request.build_absolute_uri(call.audio_file.url) if call.audio_file else None,
        "error_message": call.error_message,
    }
    return JsonResponse(response_data)
