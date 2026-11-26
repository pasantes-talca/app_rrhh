from django.http import JsonResponse


def health(request):
    return JsonResponse({"status": "ok", "service": "talca-personas", "version": "2.0.0-django"})
