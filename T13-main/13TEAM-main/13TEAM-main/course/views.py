from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Course, Enrollment, Comment, Profile
from django.http import HttpResponseForbidden
from django.shortcuts import redirect


@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={"role": "student", "full_name": request.user.username}
    )

    if request.method == "POST":
        profile.full_name = request.POST.get("full_name", "").strip()
        if request.FILES.get("avatar"):
            profile.avatar = request.FILES["avatar"]
        profile.save()
        return redirect("student_courses")

    return render(request, "profile/edit_profile.html", {"profile": profile})


@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        profile.full_name = request.POST.get('full_name')

        if request.FILES.get('avatar'):
            profile.avatar = request.FILES.get('avatar')

        profile.save()
        return redirect('student_courses')

    return render(request, 'profile/edit_profile.html', {
        'profile': profile
    })


@login_required
def after_login(request):
    role = getattr(getattr(request.user, "profile", None), "role", "student")
    if role == "teacher":
        return redirect("teacher_courses")
    return redirect("student_courses")

@login_required
def course_students(request, course_id):
    # 只能該課老師進來
    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    enrollments = Enrollment.objects.filter(course=course).select_related('student')

    # ✅ 抓該課所有留言（含回覆）
    comments = (
        Comment.objects
        .filter(course=course)
        .select_related('user')
        .prefetch_related('replies__user')
        .order_by('-created_at')
    )

    # ✅ 儲存成績（用 _action 區分，避免跟回覆留言打架）
    if request.method == 'POST' and request.POST.get('_action') == 'save_grades':
        for e in enrollments:
            mid = request.POST.get(f'mid_{e.id}', '').strip()
            fin = request.POST.get(f'final_{e.id}', '').strip()
            e.midterm = float(mid) if mid else None
            e.final = float(fin) if fin else None
            e.save()
        return redirect('course_students', course_id=course.id)

    return render(request, 'teacher/course_students.html', {
        'course': course,
        'enrollments': enrollments,
        'comments': comments,
    })


@login_required
def reply_comment(request, comment_id):
    parent = get_object_or_404(Comment, id=comment_id)

    # 只允許這門課的老師回覆
    if parent.course.teacher != request.user:
        return HttpResponseForbidden("只有這門課的老師可以回覆留言")

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(
                course=parent.course,
                user=request.user,
                content=content,
                parent=parent
            )

    return redirect('course_students', course_id=parent.course.id)

@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        profile.full_name = request.POST.get('full_name', profile.full_name).strip()

        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        profile.save()
        return redirect('edit_profile')

    return render(request, 'student/edit_profile.html', {'profile': profile})

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user != request.user:
        return HttpResponseForbidden("你不能修改別人的留言")

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            comment.content = content
            comment.save()
        return redirect('course_detail', course_id=comment.course.id)

    return render(request, 'course/edit_comment.html', {
        'comment': comment
    })
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


@login_required
def after_login(request):
    if request.user.profile.role == 'teacher':
        return redirect('teacher_courses')
    return redirect('student_courses')


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
    return render(request, 'teacher/course_list.html')


@login_required
def course_students(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    enrollments = Enrollment.objects.filter(course=course)
    comments = Comment.objects.filter(course=course).order_by('-created_at') 

    if request.method == 'POST':
        for e in enrollments:
            e.midterm = request.POST.get(f'mid_{e.id}')
            e.final = request.POST.get(f'final_{e.id}')
            e.save()

    return render(request, 'teacher/course_students.html', {
        'course': course,
        'enrollments': enrollments,
        'comments': comments,
    })


@login_required
def student_courses(request):
    courses = Course.objects.all()
    my_courses = Enrollment.objects.filter(student=request.user)
    my_course_ids = set(my_courses.values_list('course_id', flat=True))

    return render(request, 'student/course_list.html', {
        'courses': courses,
        'my_courses': my_courses,
        'my_course_ids': my_course_ids,
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

    return render(request, 'student/my_courses.html', {
        'enrollments': enrollments,
        'semester_avg': semester_avg
    })


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    comments = Comment.objects.filter(course=course).order_by('-created_at')
    enrollments = Enrollment.objects.filter(course=course)

    if request.method == 'POST':
        Comment.objects.create(
            course=course,
            user=request.user,
            content=request.POST.get('content', '').strip()
        )
        return redirect('course_detail', course_id=course.id)

    return render(request, 'course/detail.html', {
        'course': course,
        'comments': comments,
        'enrollments': enrollments,
    })