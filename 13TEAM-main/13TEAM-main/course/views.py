from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Course, Enrollment, Comment, Profile

# 註冊（學生）
def register(request):
    if request.method == 'POST':
        user = User.objects.create_user(
            username=request.POST['username'],
            password=request.POST['password']
        )
        Profile.objects.create(
            user=user,
            role='student',
            full_name=request.POST['full_name']
        )
        return redirect('login')
    return render(request, 'registration/register.html')


# ---------- 教師 ----------
@login_required
def teacher_courses(request):
    courses = Course.objects.filter(teacher=request.user)
    return render(request, 'teacher/course_list.html', {'courses': courses})


@login_required
def create_course(request):
    if request.method == 'POST':
        Course.objects.create(
            name=request.POST['name'],
            semester=request.POST['semester'],
            teacher=request.user
        )
        return redirect('teacher_courses')
    return render(request, 'teacher/course_create.html')


@login_required
def course_students(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    enrollments = Enrollment.objects.filter(course=course)

    if request.method == 'POST':
        for e in enrollments:
            e.midterm = request.POST.get(f'mid_{e.id}')
            e.final = request.POST.get(f'final_{e.id}')
            e.save()

    return render(request, 'teacher/course_students.html', {
        'course': course,
        'enrollments': enrollments
    })


# ---------- 學生 ----------
@login_required
def student_courses(request):
    courses = Course.objects.all()
    my_courses = Enrollment.objects.filter(student=request.user)
    return render(request, 'student/course_list.html', {
        'courses': courses,
        'my_courses': my_courses
    })


@login_required
def enroll(request, course_id):
    Enrollment.objects.get_or_create(
        student=request.user,
        course_id=course_id
    )
    return redirect('student_courses')


@login_required
def drop(request, course_id):
    Enrollment.objects.filter(
        student=request.user,
        course_id=course_id
    ).delete()
    return redirect('student_courses')


@login_required
def my_grades(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    avgs = [e.average() for e in enrollments if e.average() is not None]
    semester_avg = sum(avgs) / len(avgs) if avgs else None

    return render(request, 'student/my_grades.html', {
        'enrollments': enrollments,
        'semester_avg': semester_avg
    })


# ---------- 課程留言 ----------
@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    comments = Comment.objects.filter(course=course)

    if request.method == 'POST':
        Comment.objects.create(
            course=course,
            user=request.user,
            content=request.POST['content']
        )

    return render(request, 'course/detail.html', {
        'course': course,
        'comments': comments
    })
