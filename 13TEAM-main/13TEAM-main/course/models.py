from django.db import models
from django.contrib.auth.models import User

# 使用者資料（學生 / 教師）
class Profile(models.Model):
    ROLE_CHOICES = (
        ('teacher', '教師'),
        ('student', '學生'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    full_name = models.CharField(max_length=50)

    def __str__(self):
        return self.full_name


# 課程
class Course(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    semester = models.CharField(max_length=20)

    def __str__(self):
        return self.name


# 選課 + 成績
class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    midterm = models.FloatField(null=True, blank=True)
    final = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'course')

    def average(self):
        if self.midterm is not None and self.final is not None:
            return (self.midterm + self.final) / 2
        return None


# 留言
class Comment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
