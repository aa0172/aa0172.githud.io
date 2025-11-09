from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import ChatRoom, Message
from accounts.models import CustomUser


@login_required
def chat_rooms(request):
    # Получаем или создаем чат комнаты для всех комбинаций районов и интересов
    districts = [choice[0] for choice in ChatRoom.DISTRICT_CHOICES]
    interests = [choice[0] for choice in ChatRoom.INTEREST_CHOICES]

    # Создаем недостающие комнаты
    for district in districts:
        for interest in interests:
            room_name = f"{district}_{interest}"
            ChatRoom.objects.get_or_create(
                name=room_name,
                defaults={
                    'district': district,
                    'interest': interest,
                    'description': f'Чат для жителей {dict(ChatRoom.DISTRICT_CHOICES)[district]} района с интересом к {dict(ChatRoom.INTEREST_CHOICES)[interest]}'
                }
            )

    rooms = ChatRoom.objects.all().prefetch_related('active_users')

    # Рекомендуемые комнаты на основе профиля пользователя
    recommended_rooms = rooms.filter(
        district=request.user.district,
        interest=request.user.interest
    )

    # Все остальные комнаты
    other_rooms = rooms.exclude(
        district=request.user.district,
        interest=request.user.interest
    )

    context = {
        'recommended_rooms': recommended_rooms,
        'other_rooms': other_rooms,
    }
    return render(request, 'chat/rooms.html', context)


@login_required
def chat_room(request, district, interest):
    room_name = f"{district}_{interest}"
    room = get_object_or_404(ChatRoom, name=room_name)

    # Добавляем пользователя в активные
    if request.user not in room.active_users.all():
        room.active_users.add(request.user)

    # Получаем последние 50 сообщений
    messages = Message.objects.filter(room=room).select_related('user')[:50]

    # Получаем онлайн пользователей
    online_users = room.active_users.all()

    context = {
        'room': room,
        'messages': messages,
        'online_users': online_users,
    }
    return render(request, 'chat/room.html', context)


@login_required
def leave_chat(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    if request.user in room.active_users.all():
        room.active_users.remove(request.user)

    return redirect('chat_rooms')


@login_required
def get_messages(request, room_id):
    if request.method == 'GET':
        room = get_object_or_404(ChatRoom, id=room_id)
        last_message_id = request.GET.get('last_message_id', 0)

        messages = Message.objects.filter(
            room=room,
            id__gt=last_message_id
        ).select_related('user').order_by('timestamp')

        messages_data = []
        for message in messages:
            messages_data.append({
                'id': message.id,
                'user': message.user.username,
                'user_avatar': message.user.avatar.url if message.user.avatar else None,
                'content': message.content,
                'timestamp': message.timestamp.strftime('%H:%M'),
                'is_own': message.user == request.user,
            })

        return JsonResponse({'messages': messages_data})

    return JsonResponse({'error': 'Invalid request'}, status=400)