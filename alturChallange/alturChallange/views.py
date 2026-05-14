import json

from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from .models import Call
from .tasks import process_call
from .models import Call, CallStatus


def upload_list(request):
    if request.method == "POST":
        audio = request.FILES.get("audio_file")
        if not audio:
            return HttpResponseBadRequest("Missing audio_file.")

        
        create_call_from_upload(audio)
        return redirect("upload_list")

    


    calls = Call.objects.order_by("-uploaded_at")
    completed = Call.objects.filter(status="COMPLETED")
    
    # Calculate intents
    intents = {}
    total_tags = 0
    for c in completed:
        if isinstance(c.tags, dict):
            it = c.tags.get('intent', 'other')
            intents[it] = intents.get(it, 0) + 1
            total_tags += len(c.tags)

    stats = {
        "total": calls.count(),
        "completed": completed.count(),
        "avg_tags": round(total_tags / completed.count(), 1) if completed.count() > 0 else 0,
        "intents": intents
    }

    return render(request, "upload.html", {"calls": calls, "stats": stats})
    


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

def create_call_from_upload(audio):
    call = Call.objects.create(
        filename=audio.name,
        audio_file=audio
    )

    process_call.delay(str(call.id))

    return call

def api_call_export(request, call_id):
    call = get_object_or_404(Call, id=call_id)

    if request.method != "GET":
        return JsonResponse(
            {"error": "Method not allowed."},
            status=405
        )

    export_data = {
        "id": str(call.id),
        "filename": call.filename,
        "status": call.status,
        "uploaded_at": call.uploaded_at.isoformat(),
        "processed_at": (
            call.processed_at.isoformat()
            if call.processed_at
            else None
        ),
        "transcript": call.transcript,
        "summary": call.summary,
        "tags": call.tags,
        "error_message": call.error_message,
        "audio_url": (
            request.build_absolute_uri(call.audio_file.url)
            if call.audio_file
            else None
        ),
    }

    response = JsonResponse(
        export_data,
        json_dumps_params={"indent": 2}
    )

    response["Content-Disposition"] = (
        f'attachment; filename="call_{call.id}.json"'
    )

    return response

def analytics_dashboard(request):
    completed_calls = Call.objects.filter(status=CallStatus.COMPLETED)
    total_count = Call.objects.count()
    
    # Calculate Tag Distribution
    intent_counts = {}
    total_tags = 0
    
    for call in completed_calls:
        if isinstance(call.tags, dict):
            intent = call.tags.get('intent', 'unknown')
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
            total_tags += len(call.tags)

    avg_tags = total_tags / completed_calls.count() if completed_calls.exists() else 0

    context = {
        "total_calls": total_count,
        "completed_calls": completed_calls.count(),
        "avg_tags": round(avg_tags, 1),
        "intent_counts": intent_counts,
    }
    return render(request, "analytics.html", context)