from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # ✅ 首頁 / 直接導到登入頁
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False), name='index'),

    path('register/', views.register, name='register'),

    # 教師
    path('teacher/', views.teacher_courses, name='teacher_courses'),
    path('teacher/create/', views.create_course),
    path('teacher/course/<int:course_id>/', views.course_students),

    # 學生
    path('student/', views.student_courses, name='student_courses'),
    path('enroll/<int:course_id>/', views.enroll),
    path('drop/<int:course_id>/', views.drop),
    path('grades/', views.my_grades),

    # 課程
    path('course/<int:course_id>/', views.course_detail),
]
