from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class TrainingSession(models.Model):
    DISTRICT_CHOICES = [
        ('central', 'Центральный'),
        ('northern', 'Северный'),
        ('southern', 'Южный'),
        ('eastern', 'Восточный'),
        ('western', 'Западный'),
    ]

    TIME_CHOICES = [
        ('06:00', '06:00 - 08:00'),
        ('08:00', '08:00 - 10:00'),
        ('10:00', '10:00 - 12:00'),
        ('12:00', '12:00 - 14:00'),
        ('14:00', '14:00 - 16:00'),
        ('16:00', '16:00 - 18:00'),
        ('18:00', '18:00 - 20:00'),
        ('20:00', '20:00 - 22:00'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='training_sessions')
    gym_name = models.CharField(max_length=200, verbose_name='Название зала')
    description = models.TextField(blank=True, verbose_name='Описание тренировки')
    district = models.CharField(max_length=10, choices=DISTRICT_CHOICES, verbose_name='Район')
    date = models.DateField(verbose_name='Дата тренировки')
    time = models.CharField(max_length=5, choices=TIME_CHOICES, verbose_name='Время')
    max_participants = models.PositiveIntegerField(default=1, verbose_name='Максимум участников')
    current_participants = models.PositiveIntegerField(default=0, verbose_name='Текущее количество участников')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'time']
        verbose_name = 'Тренировка'
        verbose_name_plural = 'Тренировки'

    def __str__(self):
        return f"{self.user.username} - {self.gym_name} - {self.date}"

    def is_full(self):
        return self.current_participants >= self.max_participants

    def can_join(self):
        return self.is_active and not self.is_full() and self.date >= timezone.now().date()


class SessionParticipant(models.Model):
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='joined_sessions')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['session', 'user']
        verbose_name = 'Участник тренировки'
        verbose_name_plural = 'Участники тренировок'

    def __str__(self):
        return f"{self.user.username} - {self.session}"