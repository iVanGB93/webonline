from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from chat.models import Chat

class ContactView(APIView):    
    
    def get(self, queryset=None, **kwargs):
        usuario = User.objects.get(username=self.kwargs.get('pk'))
        chats = usuario.chat_set.all()
        if chats:
            chats_list = []
            for chat in chats:
                contacto = chat.participantes.all().exclude(username=usuario.username)
                contacto = contacto.values('username')[0]
                new_chat = {'id': chat.id, 'contacto': contacto['username']}
                chats_list.append(new_chat)
            return Response(data={'chats_list': chats_list}, status=status.HTTP_200_OK)
        else:
            return Response(data = {'chats_list': []}, status=status.HTTP_404_NOT_FOUND)


class AllUsersView(APIView):

    def get(self, queryset=None, **kwargs):
        usuarios = User.objects.all()
        users_list = []
        for usuario in usuarios:
            user = {'id': usuario.id, 'username': usuario.username}
            users_list.append(user)
        return Response(data={'users_list': users_list}, status=status.HTTP_200_OK)
    
    def post(self, queryset=None, **kwargs):
        user = self.kwargs.get('user')
        contact = self.kwargs.get('contact')
        if User.objects.filter(username=contact).exists():
            user = User.objects.get(username=user)
            contact = User.objects.get(username=contact)
            chats = user.chat_set.all()
            existe = False
            for chat in chats:
                if contact in chat.participantes.all():
                    chat = chat
                    existe = True
                    break
            if not existe:
                chat = Chat()
                chat.save()
                chat.participantes.add(user, contact)
            chat_id = chat.id
            img_url = contact.profile.imagen.url
            return Response(data={'chat_id': chat_id, 'img_url': img_url, 'contact': contact.username}, status=status.HTTP_200_OK)
        else:
            return Response(data = {}, status=status.HTTP_404_NOT_FOUND)