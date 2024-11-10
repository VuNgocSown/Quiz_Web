from django.shortcuts import render, redirect, get_object_or_404
# render: dùng để render template với context
# redirect: dùng để chuyển hướng người dùng đến URL khác
# get_object_or_404: dùng để lấy một đối tượng hoặc trả về lỗi 404 nếu không tìm thấy

from django.contrib.auth.decorators import login_required
# login_required: decorator yêu cầu người dùng phải đăng nhập mới có thể truy cập view

from allClass.models import MyClass
# MyClass: model từ ứng dụng allClass

from .models import Quiz, Category, Question, Option, QuizResult, StudentAnswer, QuestionGen, QuizAttempt, OptionGen, FullStudentAnswer
# Quiz, Category, Question, Option, QuizResult, StudentAnswer, QuestionGen, QuizAttempt, OptionGen, FullStudentAnswer: các model tùy chỉnh của ứng dụng hiện tại

from django.db.models import Q, Count
# Q: dùng để xây dựng các truy vấn phức tạp với các điều kiện logic

from django.utils import timezone
# timezone: cung cấp các tiện ích liên quan đến múi giờ

from django.views.decorators.cache import never_cache
# never_cache: decorator để ngăn chặn việc lưu cache cho một view cụ thể

from django.contrib.auth.decorators import user_passes_test
# user_passes_test: decorator yêu cầu người dùng phải vượt qua một kiểm tra tùy chỉnh mới có thể truy cập view

from django.http import JsonResponse
# JsonResponse: dùng để trả về dữ liệu JSON

from django.db.models import Max
# Max: dùng để tính giá trị lớn nhất của một trường trong các bản ghi

from django.db.models import OuterRef, Subquery
# OuterRef, Subquery: dùng để tạo các truy vấn con (subquery) trong Django ORM

# from quiz.models import QuizSubmission
# QuizSubmission: model từ ứng dụng quiz (đã bị comment)

from django.contrib import messages
# messages: dùng để hiển thị thông báo cho người dùng

from django.core.files.storage import FileSystemStorage
# FileSystemStorage: dùng để quản lý lưu trữ file trong hệ thống file

import pandas as pd
# pandas: thư viện phân tích dữ liệu mạnh mẽ cho Python

import openpyxl
# openpyxl: thư viện để đọc/ghi file Excel (xlsx)
# kiểm tra người dùng có phải admin hay không
def is_admin(user):
    return user.is_superuser

@login_required(login_url='login')
# hàm này dùng để render ra trang tất cả các bài quiz
def all_quiz_view(request):

    quizzes = Quiz.objects.order_by('-created_at')
    categories = Category.objects.all()

    context = {"quizzes": quizzes, "categories": categories}
    return render(request, 'all-quiz.html', context)


@login_required(login_url='login')
# hàm này dùng để render ra trang chi tiết của một bài quiz
def quiz_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if not quiz.active:
        return render(request, '404.html', {'quiz': quiz})
    questions = Question.objects.filter(quiz_id=quiz_id)
    options = []
    #  check if the user has already taken the quiz
    quiz_attempt, created = QuizAttempt.objects.get_or_create(user=request.user, quiz=quiz)
    if quiz_attempt.completed:
        return render(request, 'already_taken.html', {'quiz': quiz})
    # Chuyển đổi các đối tượng Question thành dictionary
    question_dicts = [
        {
            'id': question.id,
            'question_text': question.question_text,
            'question_type': question.question_type,
            'category': question.category.id if question.category else None,
            'topic': question.topic,
            'subtopic': question.subtopic,
            'CLO': question.CLO,
            'quiz_id': question.quiz_id.id,
            'difficulty': question.difficulty
        } 
        for question in questions
    ]
    if 'quiz_id' in request.session and request.session['quiz_id'] != quiz_id:
        request.session['quiz_id'] = quiz_id
        del request.session['options']
    else:
        request.session['quiz_id'] = quiz_id
    if 'options' in request.session and options != []:
        options = request.session['options']
        print("in ra")
    else:
        for question in questions:
            correct_option = Option.objects.filter(question_id=question, is_correct=True).order_by('?').first()
            incorrect_options = Option.objects.filter(question_id=question, is_correct=False).order_by('?')[:3]

            # print(correct_option, incorrect_options)
            # print("Vu Ngoc Son")
            if correct_option is None or len(incorrect_options) < 3:
                continue
            # Chuyển đổi các đối tượng Option thành dictionary
            option_dicts = [
                {
                    'id': opt.id,
                    'option_text': opt.option_text,
                    'question_id': opt.question_id.id,
                    'is_correct': opt.is_correct
                } 
                for opt in [correct_option] + list(incorrect_options)
            ]
            options.append(option_dicts)
        
        # Lưu các câu trả lời vào session
        request.session['options'] = options
    if not questions.exists():
        return render(request, 'quiz.html', {'quiz': quiz, 'questions': question_dicts, 'options': options, 'quiz_result': None, 'error': 'No questions available for this quiz.'})
    
    try: 
        quiz_result = QuizResult.objects.filter(user_id=request.user, quiz_id=quiz).order_by('-id').first()
        if quiz_result:
            elapsed_time = (timezone.now() - quiz_result.start_time).total_seconds()
            if elapsed_time > quiz.duration * 60:
                raise QuizResult.DoesNotExist
        else:
            raise QuizResult.DoesNotExist
    except QuizResult.DoesNotExist:
        quiz_result = QuizResult.objects.create(
            user_id=request.user,
            score=0,
            correct_answers=0,
            incorrect_answers=0,
            quiz_id=quiz,
            start_time=timezone.now()
        )
    elapsed_time = (timezone.now() - quiz_result.start_time).total_seconds()
    remaining_time = max(quiz.duration * 60 - elapsed_time, 0)
    return render(request, 'quiz.html', 
                  {'quiz': quiz, 
                   'questions': question_dicts, 
                   'options': options, 
                   'quiz_result': quiz_result,
                   'remaining_time': remaining_time,
                   })
# hàm này dùng để xử lý việc người dùng gửi đã gửi câu trả lời của bài quiz(người dùng đã làm bài này hay chưa)
def already_taken(request):
    return render(request, 'already_taken.html')

@login_required(login_url='login')
@never_cache
# hàm này dùng để xử lý việc người dùng gửi câu trả lời của bài quiz(xem kết quă)
def quiz_result_view(request, quiz_id, quiz_result_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = Question.objects.filter(quiz_id=quiz_id)
    quiz_result = get_object_or_404(QuizResult, id=quiz_result_id)
    user = request.user
    quiz_attempt, created = QuizAttempt.objects.get_or_create(user=user, quiz=quiz)
    if quiz_attempt.completed:
        return render(request, 'already_taken.html', {'quiz': quiz})
    if request.method == 'POST':
        quiz_result.end_time = timezone.now()
        score = 0
        correct_answers = 0
        incorrect_answers = 0
        heso = 10 / len(questions)
        for question in questions:
            if question.question_type == 'MCQ':
                selected_option_id = request.POST.get(str(question.id))
                if selected_option_id:
                    selected_option = Option.objects.get(id=int(selected_option_id))
                    options = request.session['options']
                    options_of_question = [opt for opt in options if opt[0]['question_id'] == question.id]
                    if len(options_of_question) == 0:
                        continue
                    option_1 = Option.objects.filter(id=options_of_question[0][0]['id']).first()
                    option_2 = Option.objects.filter(id=options_of_question[0][1]['id']).first()
                    option_3 = Option.objects.filter(id=options_of_question[0][2]['id']).first()
                    option_4 = Option.objects.filter(id=options_of_question[0][3]['id']).first()
                    FullStudentAnswer.objects.create(
                        question_id=question,
                        quiz_result_id=quiz_result,
                        selected_option=selected_option,
                        option_1=option_1,
                        option_2=option_2,
                        option_3=option_3,
                        option_4=option_4,
                        quiz_id=quiz
                    )
                    if selected_option.is_correct:
                        score += heso
                        correct_answers += 1
                    else:
                        incorrect_answers += 1
            elif question.question_type == 'FIB':
                answer_text = request.POST.get(str(question.id))
                if answer_text:
                    FullStudentAnswer.objects.create(
                        question_id=question,
                        quiz_result_id=quiz_result,
                        answer_text=answer_text,
                        quiz_id=quiz
                    )
                    StudentAnswer.objects.create(
                        question_id=question,
                        quiz_result_id=quiz_result,
                        answer_text=answer_text,
                        studen_id=request.user.profile.studen_id,
                        quiz_id=quiz
                    )
        quiz_result.score = score
        quiz_result.correct_answers = correct_answers
        quiz_result.incorrect_answers = incorrect_answers
        quiz_result.save()
        quiz_attempt.completed = True
        quiz_attempt.save()
    return render(request, 'quiz_result.html', {
        'score': score, 
        'correct_answers': correct_answers,
        'incorrect_answers': incorrect_answers,
        'username': request.user.username,
        'total_questions': len(questions),
        'quiz': quiz,
        'quiz_result': quiz_result
    })

@login_required(login_url='login')
@user_passes_test(is_admin)
# hàm này dùng để render ra trang thêm bài quiz
def addQuiz(request, class_id):
    myclass = get_object_or_404(MyClass, id=class_id)
    categories = Category.objects.all()
    return render(request, 'addQuiz.html',{'categories': categories,
                                           'class_id': class_id,
                                           'myclass': myclass})

@login_required(login_url='login')
@user_passes_test(is_admin)
# hàm này dùng để xử lý kết qủa bài thi và in ra bảng xếp hạng
def quiz_leaderboard_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    subquery = QuizResult.objects.filter(
    user_id=OuterRef('user_id'),  
    quiz_id=OuterRef('quiz_id')   
    ).order_by('-score').values('score')[:1]
    results = QuizResult.objects.filter(score = Subquery(subquery), quiz_id = quiz_id).order_by('-score')   
    print(results)
    return render(request, 
                  'quiz_leaderboard.html', 
                  { 'quiz': quiz,
                    'results': results})

@login_required(login_url='login')
@user_passes_test(is_admin)
#  hàm này có chức năng tạo ra đề kiểm tra từ cơ sở dữ liệu câu hỏi hiện có
def create_quiz_from_db(request, class_id):
    myclass = get_object_or_404(MyClass, id=class_id)
    categories = Category.objects.all()
    questions = QuestionGen.objects.all()
    valid_questions = []
    for question in questions:
        if question.question_type == 'MCQ':
            options = OptionGen.objects.filter(question_id=question.id)
            num_correct_options = options.filter(is_correct=True).count()
            num_incorrect_options = options.filter(is_correct=False).count()
            print(question.question_text, num_correct_options, num_incorrect_options)
            if num_correct_options >= 1 and num_incorrect_options >= 3:
                valid_questions.append(question)
        else:
            valid_questions.append(question)
    questions = QuestionGen.objects.filter(id__in=[question.id for question in valid_questions])
    if request.method == 'POST':
        quiz_title = request.POST.get('quiz_title')
        quiz_description = request.POST.get('quiz_description')
        quiz_category = request.POST.get('quiz_category')
        quiz_duration = request.POST.get('quiz_duration')  # Get duration from form
        selected_questions = request.POST.getlist('questions')
        quiz = Quiz.objects.create(
            title=quiz_title,
            description=quiz_description,
            category_id=quiz_category,
            duration=quiz_duration,
            total_questions=len(selected_questions),
            instructor=request.user,
            class_id=myclass
        )
        for question_id in selected_questions:
            question = QuestionGen.objects.get(id=question_id)
            question = Question.objects.create(
                quiz_id=quiz,
                question_text=question.question_text,
                CLO=question.CLO,
                difficulty=question.difficulty,
                question_type=question.question_type,
                topic=question.topic,
                subtopic=question.subtopic
            )
            if question.question_type == 'MCQ':
                options = OptionGen.objects.filter(question_id=question_id)
                for option in options:
                    Option.objects.create(
                        question_id=question,
                        option_text=option.option_text,
                        is_correct=option.is_correct
                    )
        messages.success(request, 'Quiz created successfully!')
        return redirect('class_detail', class_id=myclass.id)
    if 'category' in request.GET:
        category_filter = request.GET['category'].split(',')
        questions = questions.filter(category_id__in=category_filter)
    if 'clo' in request.GET:
        clo_filter = request.GET['clo'].split(',')
        questions = questions.filter(CLO__in=clo_filter)
    if 'difficulty' in request.GET:
        difficulty_filter = request.GET['difficulty'].split(',')
        questions = questions.filter(difficulty__in=difficulty_filter)
    if 'type' in request.GET:
        type_filter = request.GET['type'].split(',')
        questions = questions.filter(question_type__in=type_filter)
    if 'topic' in request.GET:
        topic_filter = request.GET['topic'].split(',')
        questions = questions.filter(topic__in=topic_filter)
    if 'subtopic' in request.GET:
        subtopic_filter = request.GET['subtopic'].split(',')
        questions = questions.filter(subtopic__in=subtopic_filter)
    # Lấy các giá trị duy nhất cho các bộ lọc
    clos = questions.values_list('CLO', flat=True).distinct()
    topics = questions.values_list('topic', flat=True).distinct()
    subtopics = questions.values_list('subtopic', flat=True).distinct()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        questions_data = list(questions.values('id', 'question_text', 'CLO', 'difficulty', 'question_type'))
        return JsonResponse({'questions': questions_data})
    context = {
        'categories': categories,
        'clos': clos,
        'topics': topics,
        'subtopics': subtopics,
        'questions': questions,
        'class_id': class_id
    }
    return render(request, 'createQuizFromDB.html', context)
@login_required(login_url='login')
@user_passes_test(is_admin)
# hàm này có chức năng cho phép giáo viên chấm các câu hỏi tự luận của sinh viên, có thể lấy câu trả lời làm đáp án lưu trong cơ sở dữ liệu
def mark_quiz(request, class_id, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = Question.objects.filter(quiz_id = quiz_id)
    text_questions = Question.objects.filter(quiz_id=quiz_id, question_type='FIB')
    text_answers = StudentAnswer.objects.filter(question_id__in=text_questions, is_mark=False)
    heso = 10/len(questions)
    if request.method == 'POST':
        for answer in text_answers:
            is_correct = request.POST.get(f'correct_{answer.id}')
            filled_score = request.POST.get(f'score_{answer.id}')
            if is_correct == 'true':
                answer.score += heso
            if filled_score:
                answer.score = float(filled_score)
            if is_correct != None or filled_score != None:
                answer.is_mark = True
            answer.save()
            add_option = request.POST.get(f'option_{answer.id}')
            if add_option:
                question = Question.objects.get(id=answer.question_id_id)
                print(question, question.question_text)
                if not QuestionGen.objects.filter(question_text=question.question_text, question_type = 'MCQ').exists():
                    new_question = QuestionGen.objects.create(
                            question_text=question.question_text,
                            CLO=question.CLO,
                            difficulty=question.difficulty,
                            question_type='MCQ',
                            category=question.quiz_id.category,
                            topic=question.topic,
                            subtopic=question.subtopic
                        )
                    new_question.save()
                    OptionGen.objects.create(
                        question_id=new_question,
                        option_text=answer.answer_text,
                        is_correct=answer.is_mark
                    )
                else:
                    old_question = QuestionGen.objects.get(question_text=question.question_text, question_type = 'MCQ')
                    OptionGen.objects.create(
                        question_id=old_question,
                        option_text=answer.answer_text,
                        is_correct=answer.is_mark
                    )
        for quiz_result in QuizResult.objects.filter(quiz_id=quiz_id):
            text_score = sum([answer.score for answer in text_answers if answer.quiz_result_id == quiz_result])
            quiz_result.score += text_score
            quiz_result.save()
        return redirect('class_detail', class_id=class_id)
    return render(request, 'mark_quiz.html', {'quiz': quiz, 
                                              'text_answers': text_answers, 
                                              'text_questions': text_questions,
                                              'heso': heso,
                                              'class_id': class_id
                                              })

@login_required(login_url='login')
@user_passes_test(is_admin)
# thông báo đã tải đề thi lên thành công
def upload_success(request):
    return render(request, 'upload_success.html')

@login_required(login_url='login')
def upload_error(request):
    return render(request, 'upload_error.html')
    
@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)
# lấy các câu hỏi từ file excel tải lên để lưu vào cơ sở dữ liệu
def create_quiz_from_excel(request):
    categories = Category.objects.all()
    if request.method == 'POST' and request.FILES['quiz_file']:
        quiz_file = request.FILES['quiz_file']
        category_id = request.POST.get('category')
        category = Category.objects.get(id=category_id)
        
        # Đọc file Excel và sử dụng hàng đầu tiên làm tiêu đề cột
        try:
            df = pd.read_excel(quiz_file)
        except Exception as e:
            return render(request, 'upload_error.html', {'error': 'Can not read from file.'})

        # Xóa tất cả các cột toàn NaN
        df = df.dropna(axis=1, how='all')

        # Lọc các hàng mà cột đầu tiên là 'TEXT' hoặc 'PARAGRAPH'
        df_filtered = df.iloc[1:][(df.iloc[1:, 0].str.upper() == 'TEXT') | (df.iloc[1:, 0].str.upper() == 'PARAGRAPH')]

        # Kiểm tra xem DataFrame đã lọc có đủ hàng không
        if df_filtered.empty:
            return render(request, 'upload_error.html', {'error': 'Không có hàng nào phù hợp trong file Excel.'})

        # Xóa tất cả các hàng có topic, subtopic, CLOx, DifLevel bằng NaN

        df_filtered = df_filtered.dropna(subset=['Topic', 'SubTopic', 'CLOx', 'DifLevel'])

        # Lấy các giá trị từ các cột cần thiết
        question_type = 'FIB'
        question_texts = df_filtered.iloc[:, 1]

        try:
            Topic = df_filtered.filter(like='Topic', axis=1).iloc[:, 0]
        except IndexError:
            return render(request, 'upload_error.html', {'error': 'Không tìm thấy cột "topic".'})

        try:
            SubTopic = df_filtered.filter(like='SubTopic', axis=1).iloc[:, 0]
        except IndexError:
            return render(request, 'upload_error.html', {'error': 'Không tìm thấy cột "subtopic".'})

        try:
            # CLO = df_filtered.filter(like='CLOx', axis=1).iloc[:, 0]
            CLO = df_filtered.filter(like='CLOx', axis=1).iloc[:, 0].str.extract(r'(\d+)')[0]
        except IndexError:
            return render(request, 'upload_error.html', {'error': 'Không tìm thấy cột "CLOx".'})

        try:
            difficulty = df_filtered.filter(like='DifLevel', axis=1).iloc[:, 0]
        except IndexError:
            return render(request, 'upload_error.html', {'error': 'Không tìm thấy cột "DifLevel".'})

        # Lưu các câu hỏi vào model QuestionGen
        for i in range(len(df_filtered)):
            QuestionGen.objects.create(
                question_type=question_type,
                question_text=question_texts.iloc[i],
                topic=Topic.iloc[i],
                subtopic=SubTopic.iloc[i],
                CLO=CLO.iloc[i],
                difficulty=difficulty.iloc[i],
                category=category
            )
        
        return redirect('upload_success')
    return render(request, 'addquiz')
@login_required(login_url='login')
# xem chi tiết lại bài thi và đáp án mà sinh viên đã làm sau khi đã nộp bài thi
def all_quiz_result_view(request, quiz_id, quiz_result_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = Question.objects.filter(quiz_id=quiz_id)
    quiz_result = get_object_or_404(QuizResult, id=quiz_result_id)
    full_student_answers = FullStudentAnswer.objects.filter(quiz_result_id=quiz_result_id)
    return render(request, 'all_student_answers.html', {
        'quiz': quiz,
        'questions': questions,
        'quiz_result': quiz_result,
        'full_student_answers': full_student_answers
    })

@login_required(login_url='login')
#  dùng để cho phép giáo viên kích hoạt bài kiểm tra, cho phép sinh viên có thể vào làm bài
def activate_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.user == quiz.instructor:
        if request.method == 'POST':
            quiz.active = 'active' in request.POST
            quiz.save()
    # Get the MyClass instance associated with this quiz
    my_class = quiz.class_id  # Use the correct field name
    if my_class:
        return redirect('class_detail', class_id=my_class.id)
    else:
        messages.error(request, 'This quiz is not associated with any class.')
        return redirect('my_classes')