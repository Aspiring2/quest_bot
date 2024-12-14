from django.db import models

# Локация
class Location(models.Model):
    name = models.CharField(max_length=255)  # Название локации
    description = models.TextField(blank=True, null=True)  # Описание локации
    hint_cost = models.IntegerField(default=10)  # Стоимость подсказки (в монетах)
    order = models.PositiveIntegerField(default=0)  # Очередность локации

    class Meta:
        ordering = ['order']  # Сортировка по очередности

    def __str__(self):
        return self.name


# Пользователь
class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True)  # Уникальный Telegram ID
    username = models.CharField(max_length=255, null=True, blank=True)  # Имя пользователя
    coins = models.IntegerField(default=0)  # Количество монет
    current_scenario = models.ForeignKey(
        'Scenario',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='active_users',
    )  # Текущий сценарий

    def __str__(self):
        return f"{self.username} ({self.telegram_id}) - {self.coins} монет"


# Задача
class Task(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='tasks')  # Локация
    reward = models.IntegerField(default=10)  # Награда за выполнение задачи
    task_type = models.CharField(
        max_length=50,
        choices=(
            ('riddle', 'Загадка'),
            ('puzzle', 'Ребус'),
            ('poem', 'Стих'),
            ('message', 'Сообщение'),  # Новый тип задачи
        ),
    )
    text = models.TextField(null=True, blank=True)  # Текст задачи (сообщение)
    image = models.ImageField(upload_to='tasks/', null=True, blank=True)  # Картинка задачи
    answer = models.CharField(max_length=255, null=True, blank=True)  # Ответ (необязательно)
    order = models.PositiveIntegerField(default=0)  # Очередность задачи в локации

    class Meta:
        ordering = ['order']  # Сортировка по очередности

    def __str__(self):
        return f"{self.get_task_type_display()} in {self.location.name}"


# Подсказка
class Hint(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='hints'
    )  # Связь с задачей
    text = models.TextField(null=True, blank=True)  # Текст подсказки
    image = models.ImageField(upload_to='hints/', null=True, blank=True)  # Картинка для подсказки (опционально)
    cost = models.IntegerField(default=5)  # Стоимость подсказки (в монетах)
    order = models.PositiveIntegerField(default=0)  # Очередность подсказки

    class Meta:
        ordering = ['order']  # Сортировка по очередности

    def __str__(self):
        return f"Hint for Task {self.task.id} - {self.text[:30]}..."


# Сценарий
class Scenario(models.Model):
    name = models.CharField(max_length=255)  # Название сценария
    description = models.TextField(blank=True, null=True)  # Описание сценария
    locations = models.ManyToManyField(Location, through='ScenarioStep', related_name='scenarios')  # Локации в сценарии

    def __str__(self):
        return self.name


# Шаг сценария
class ScenarioStep(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name='steps')  # Сценарий
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='scenario_steps')  # Локация
    order = models.IntegerField()  # Порядок шага

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Step {self.order} in {self.scenario.name}"


# Прогресс пользователя
class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')  # Пользователь
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name='user_progress')  # Сценарий
    current_step = models.ForeignKey(
        ScenarioStep, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_progress'
    )  # Текущий шаг
    is_completed = models.BooleanField(default=False)  # Завершён ли сценарий

    def __str__(self):
        return f"{self.user.username} - {self.scenario.name} (Step {self.current_step.order if self.current_step else 'N/A'})"
