import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def log_from_frontend(request):
    try:
        log_data = json.loads(request.body)
        level = log_data.get('level', None)
        message = log_data.get('message')
        method_name = log_data.get('methodName')
        date = log_data.get('date')

        if level.lower() == 'critical':
            logger.critical(message, method_name, date)
        else:
            logger.error(message, method_name, date)

        return JsonResponse(status=200)
    except Exception as e:
        logger.error(e)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
