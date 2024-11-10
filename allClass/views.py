# views.py
from django.shortcuts import render, redirect, get_object_or_404
# render: dùng để render template với context
# redirect: dùng để chuyển hướng người dùng đến URL khác
# get_object_or_404: dùng để lấy một đối tượng hoặc trả về lỗi 404 nếu không tìm thấy

from django.contrib.auth.decorators import login_required
# login_required: decorator yêu cầu người dùng phải đăng nhập mới có thể truy cập view

from django.contrib import messages
# messages: dùng để hiển thị thông báo cho người dùng

from .models import MyClass, ClassRequest
# MyClass, ClassRequest: các model tùy chỉnh của ứng dụng

from quiz.models import Quiz
# Quiz: model từ ứng dụng quiz

from .forms import ClassRequestForm, CreateClassForm
# ClassRequestForm, CreateClassForm: các form tùy chỉnh của ứng dụng

from account.models import User
# User: model người dùng từ ứng dụng account

import pandas as pd
# pandas: thư viện phân tích dữ liệu mạnh mẽ cho Python

from django.http import JsonResponse
# JsonResponse: dùng để trả về dữ liệu JSON

from django.http import HttpResponse
# HttpResponse: dùng để trả về một phản hồi HTTP

@login_required(login_url='login')
# hàm này dùng để render ra trang tất cả các lớp học mà người dùng đã tham gia hoặc tạo
def my_classes(request):
    user = request.user
    if user.is_staff:
        classes = MyClass.objects.filter(instructor=user)
    else:
        classes = user.classes.all()
    if not classes:
        messages.info(request, 'No classes found.')
    return render(request, 'myClass.html', {'classes': classes})

@login_required(login_url='login')
# hàm này dùng để xử lý việc người dùng gửi yêu cầu tham gia lớp học
def request_class(request):
    if request.method == 'POST':
        form = ClassRequestForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                myclass = MyClass.objects.get(code=code)
                if request.user in myclass.students.all():
                    messages.info(request, 'You are already in this class.')
                else:
                    ClassRequest.objects.create(student=request.user, myclass=myclass)
                    messages.success(request, 'Your request has been sent.')
                return redirect('my_classes')
            except MyClass.DoesNotExist:
                messages.error(request, 'Invalid class code.')
    else:
        form = ClassRequestForm()
    
    user = request.user
    if user.is_staff:
        classes = MyClass.objects.filter(instructor=user)
    else:
        classes = user.classes.all()
    
    return render(request, 'myClass.html', {'form': form, 'classes': classes})

@login_required(login_url='login')
# hàm này dùng để xử lý việc người dùng tạo lớp học mới
def create_class(request):
    if request.method == 'POST':
        form = CreateClassForm(request.POST)
        if form.is_valid():
            myclass = form.save(commit=False)
            myclass.instructor = request.user
            myclass.save()
            messages.success(request, 'Class created successfully.')
            return redirect('my_classes')
    else:
        form = CreateClassForm()
    
    user = request.user
    if user.is_staff:
        classes = MyClass.objects.filter(instructor=user)
    else:
        classes = user.classes.all()
    
    return render(request, 'myClass.html', {'form': form, 'classes': classes})

@login_required(login_url='login')
# hàm này dùng để render ra trang chi tiết của một lớp học
def class_detail(request, class_id):
    myclass = get_object_or_404(MyClass, id=class_id)
    # Kiểm tra quyền truy cập
    if request.user != myclass.instructor and request.user not in myclass.students.all():
        raise Http404("You do not have permission to access this class.")
    class_requests = ClassRequest.objects.filter(myclass=myclass, approved=False)
    quizzes = Quiz.objects.filter(class_id=myclass.id)
    student_count = myclass.students.count()
    student_list = myclass.students.all()
    instructor = myclass.instructor
    return render(request, 'inyourclass.html', {'class': myclass, 'class_requests': class_requests, 'quizzes': quizzes,'student_count': student_count,'student_list': student_list,'instructor': instructor, 'class_id': class_id})

@login_required(login_url='login')
# hàm này dùng để xử lý việc người dùng gửi yêu cầu tham gia lớp học
def approve_request(request, request_id):
    class_request = get_object_or_404(ClassRequest, id=request_id)
    if request.user == class_request.myclass.instructor:
        class_request.approved = True
        class_request.myclass.students.add(class_request.student)
        class_request.save()
        messages.success(request, 'Request approved.')
    else:
        messages.error(request, 'You are not authorized to approve this request.')
    return redirect('class_detail', class_id=class_request.myclass.id)

@login_required(login_url='login')
# hàm này dùng để xử lý việc người dùng từ chối yêu cầu tham gia lớp học
def reject_request(request, request_id):
    class_request = get_object_or_404(ClassRequest, id=request_id)
    if request.user == class_request.myclass.instructor:
        class_request.delete()
        messages.success(request, 'Request rejected.')
    else:
        messages.error(request, 'You are not authorized to reject this request.')
    return redirect('class_detail', class_id=class_request.myclass.id)

@login_required(login_url='login')
# hàm này dùng để xử lý việc người dùng từ chối tất cả các yêu cầu tham gia lớp học
def approve_all_requests(request, class_id):
    myclass = get_object_or_404(MyClass, id=class_id)
    if request.user == myclass.instructor:
        class_requests = ClassRequest.objects.filter(myclass=myclass, approved=False)
        for class_request in class_requests:
            class_request.approved = True
            class_request.myclass.students.add(class_request.student)
            class_request.save()
        messages.success(request, 'All requests approved.')
    else:
        messages.error(request, 'You are not authorized to approve these requests.')
    return redirect('class_detail', class_id=myclass.id)

@login_required(login_url='login')
# hàm này dùng để xử lý việc giáo viên thêm sinh viên vào lớp học(thêm thủ công)
def add_members(request, class_id):
    myclass = get_object_or_404(MyClass, id=class_id)
    if request.user != myclass.instructor:
        messages.error(request, 'You are not authorized to add members to this class.')
        return redirect('class_detail', class_id=class_id)

    if request.method == 'POST':
        usernames = request.POST.getlist('usernames')
        added_members = []
        not_found_members = []

        for username in usernames:
            try:
                user = User.objects.get(username=username)
                if user not in myclass.students.all():
                    myclass.students.add(user)
                    added_members.append(username)
            except User.DoesNotExist:
                not_found_members.append(username)

        if added_members:
            messages.success(request, f'Successfully added {len(added_members)} members.')
        if not_found_members:
            messages.error(request, f'The following usernames were not found: {", ".join(not_found_members)}')

        return redirect('class_detail', class_id=class_id)

    return redirect('class_detail', class_id=class_id)

@login_required(login_url='login')
# hàm này dùng để xử lý việc giáo viên thêm sinh viên vào lớp học(thêm hàng loạt từ file excel)
def import_members(request, class_id):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        df = pd.read_excel(file)

        # Tìm dòng có giá trị "Mã SV" (không phân biệt chữ hoa chữ thường)
        index = df.apply(lambda row: row.astype(str).str.contains('mã sv', case=False).any(), axis=1).idxmax()
        usernames = df.iloc[index + 1:, 1].dropna().tolist()

        return JsonResponse({'success': True, 'usernames': usernames})
    return JsonResponse({'success': False, 'error': 'Invalid file or no file uploaded'})


@login_required(login_url='login')
# hàm này dùng để xử lý việc giáo viên xuất ra danh sách tài khoản sinh viên trong lớp bao gồm tài khoản và mật khẩu mặc định
def export_members(request, class_id):
    myclass = get_object_or_404(MyClass, id=class_id)
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You are not authorized to export members of this class.')
        return redirect('class_detail', class_id=class_id)

    students = myclass.students.all()
    data = []
    for student in students:
        if not student.is_staff and not student.is_superuser:
            data.append({
                'Username': student.username,
                'First Name': student.first_name,
                'Last Name': student.last_name,
                'Email': student.email,
                'Password': student.username+"@PTIT",
            })

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{myclass.name}_members.xlsx"'
    df.to_excel(response, index=False)
    return response