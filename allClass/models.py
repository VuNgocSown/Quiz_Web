from django.db import models
from django.contrib.auth.models import User
from account.models import Profile
# Create your models here.
class MyClass(models.Model):
    name = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='instructed_classes')
    students = models.ManyToManyField(User, related_name='classes')
    code = models.CharField(max_length=10, unique=True, null=True)
    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"
    def __str__(self):
        return self.name

class ClassRequest(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='class_requests')
    myclass = models.ForeignKey(MyClass, on_delete=models.CASCADE, related_name='class_requests')
    approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'myclass')

    def __str__(self):
        return f"{self.student.username} - {self.myclass.name}"