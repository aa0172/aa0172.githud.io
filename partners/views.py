from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import TrainingSession, SessionParticipant
from accounts.models import CustomUser


def home(request):
    if request.user.is_authenticated:
        # Показываем активные тренировки пользователя
        user_sessions = TrainingSession.objects.filter(
            user=request.user,
            is_active=True,
            date__gte=timezone.now().date()
        )[:5]

        # Показываем рекомендованных пользователей
        recommended_users = CustomUser.objects.exclude(id=request.user.id).filter(
            district=request.user.district,
            interest=request.user.interest
        )[:6]
    else:
        user_sessions = TrainingSession.objects.none()
        recommended_users = CustomUser.objects.none()

    context = {
        'user_sessions': user_sessions,
        'recommended_users': recommended_users,
    }
    return render(request, 'partners/home.html', context)


@login_required
def search_partners(request):
    users = CustomUser.objects.exclude(id=request.user.id)

    # Фильтрация по параметрам
    district = request.GET.get('district')
    interest = request.GET.get('interest')
    age_group = request.GET.get('age_group')

    if district:
        users = users.filter(district=district)
    if interest:
        users = users.filter(interest=interest)
    if age_group:
        users = users.filter(age_group=age_group)

    # Поиск по имени/фамилии
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    context = {
        'users': users,
        'current_filters': {
            'district': district,
            'interest': interest,
            'age_group': age_group,
            'search': search_query,
        }
    }
    return render(request, 'partners/search.html', context)


@login_required
def create_session(request):
    if request.method == 'POST':
        gym_name = request.POST.get('gym_name')
        description = request.POST.get('description')
        district = request.POST.get('district')
        date = request.POST.get('date')
        time = request.POST.get('time')
        max_participants = request.POST.get('max_participants', 1)

        if gym_name and district and date and time:
            session = TrainingSession.objects.create(
                user=request.user,
                gym_name=gym_name,
                description=description,
                district=district,
                date=date,
                time=time,
                max_participants=max_participants
            )
            messages.success(request, 'Тренировка успешно создана!')
            return redirect('home')
        else:
            messages.error(request, 'Пожалуйста, заполните все обязательные поля.')

    return render(request, 'partners/create_session.html')


@login_required
def join_session(request, session_id):
    session = get_object_or_404(TrainingSession, id=session_id)

    if not session.can_join():
        messages.error(request, 'Невозможно присоединиться к этой тренировке.')
        return redirect('search_partners')

    if SessionParticipant.objects.filter(session=session, user=request.user).exists():
        messages.warning(request, 'Вы уже присоединились к этой тренировке.')
        return redirect('search_partners')

    SessionParticipant.objects.create(session=session, user=request.user)
    session.current_participants += 1
    session.save()

    messages.success(request, f'Вы успешно присоединились к тренировке в {session.gym_name}!')
    return redirect('search_partners')