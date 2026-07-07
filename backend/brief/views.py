import logging

from openai import OpenAIError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .config import BriefRequestSerializer
from .services import generate_brief

logger = logging.getLogger(__name__)


class GenerateBriefView(APIView):
    def post(self, request):
        serializer = BriefRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = generate_brief(serializer.validated_data)
        except OpenAIError:
            logger.exception("OpenAI request failed")
            return Response(
                {"error": "Brief generation is temporarily unavailable."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except ValueError:
            logger.exception("Malformed model output")
            return Response(
                {"error": "Received an invalid brief from the model. Please retry."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(result, status=status.HTTP_200_OK)
