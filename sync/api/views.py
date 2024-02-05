from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json

class StatusCheckView(APIView):

    def get(self, request, **kwargs):
        name = self.kwargs.get('name')
        data = {'status': True, 'message': f'check completed {name}'}
        return Response(status=status.HTTP_200_OK, data=json.dumps(data))