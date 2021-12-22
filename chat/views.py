from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth.models import User

from .models import Chat

@login_required(login_url='/users/login/')
def index(request):
    content = {'usuarios': User.objects.all()}
    return render(request, 'chat/index.html', content)

@login_required(login_url='/users/login/')
def room(request, username=None):
    if username == None:
        content = {'usuarios': User.objects.all()}
        return render(request, 'chat/index.html', content)
    if User.objects.filter(username=username).exists():
        usuario2 = User.objects.get(username=username)
        chats = request.user.chat_set.all()
        existe = False
        for chat in chats:
            if usuario2 in chat.participantes.all():
                chat = chat
                existe = True
                break
        if not existe:
            chat = Chat()
            chat.save()
            chat.participantes.add(request.user, usuario2)
        chat_id = chat.id
        img_url = usuario2.profile.imagen.url
        if not request.user in chat.participantes.all():
            return redirect('chat:index')
        return render(request, 'chat/index.html', {
            'chat_id': chat_id,
            'img_url': img_url,
            'usuario2': usuario2,
        })
    else:
        return redirect('chat:index')