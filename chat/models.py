from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatRoom(models.Model):
    DISTRICT_CHOICES = [
        ('central', 'Центральный'),
        ('northern', 'Северный'),
        ('southern', 'Южный'),
        ('eastern', 'Восточный'),
        ('western', 'Западный'),
    ]

    INTEREST_CHOICES = [
        ('music', 'Музыка'),
        ('games', 'Компьютерные игры'),
        ('science', 'Наука'),
        ('books', 'Книги'),
        ('parties', 'Тусовки'),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name='Название комнаты')
    district = models.CharField(max_length=10, choices=DISTRICT_CHOICES, verbose_name='Район')
    interest = models.CharField(max_length=10, choices=INTEREST_CHOICES, verbose_name='Интерес')
    description = models.TextField(blank=True, verbose_name='Описание чата')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    active_users = models.ManyToManyField(User, blank=True, related_name='active_chats',
                                          verbose_name='Активные пользователи')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Чат комната'
        verbose_name_plural = 'Чат комнаты'
        unique_together = ['district', 'interest']

    def __str__(self):
        return f"{self.get_district_display()} - {self.get_interest_display()}"

    def get_display_name(self):
        return f"Чат {self.get_district_display()} района - {self.get_interest_display()}"

    def get_user_count(self):
        return self.active_users.count()

    def get_last_message(self):
        return self.messages.order_by('-timestamp').first()


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', verbose_name='Комната')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages', verbose_name='Пользователь')
    content = models.TextField(verbose_name='Сообщение')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время отправки')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}..."

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()