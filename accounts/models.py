from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
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

    AGE_GROUP_CHOICES = [
        ('15-18', '15-18 лет'),
        ('19-27', '19-27 лет'),
        ('28-39', '28-39 лет'),
        ('40+', '40+ лет'),
    ]

    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    first_name = models.CharField(max_length=30, blank=True, verbose_name='Имя')
    last_name = models.CharField(max_length=30, blank=True, verbose_name='Фамилия')
    district = models.CharField(max_length=10, choices=DISTRICT_CHOICES, default='central', verbose_name='Район')
    interest = models.CharField(max_length=10, choices=INTEREST_CHOICES, default='music', verbose_name='Интерес')
    age_group = models.CharField(max_length=5, choices=AGE_GROUP_CHOICES, default='19-27',
                                 verbose_name='Возрастная группа')

    def __str__(self):
        return self.username

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username