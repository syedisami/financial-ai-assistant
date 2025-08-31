from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model with role-based access"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        help_text='User role determines access level'
    )
    
    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'chatbot_customuser'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Log(models.Model):
    """Log all chat interactions for audit purposes"""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    question = models.TextField(
        help_text='Original user question'
    )
    sql = models.TextField(
        help_text='Generated SQL query'
    )
    answer = models.TextField(
        help_text='Response provided to user'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text='When this interaction occurred'
    )
    
    def __str__(self):
        return f"{self.user.username}: {self.question[:50]}..."
    
    class Meta:
        db_table = 'chatbot_log'
        verbose_name = 'Chat Log'
        verbose_name_plural = 'Chat Logs'
        ordering = ['-timestamp']
