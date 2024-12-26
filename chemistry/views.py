from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import Grade, Section, Category, Question
from .forms import QuestionForm, VariantCreationForm
# import locale
from reportlab.pdfgen import canvas #для створення pdf з питаннями
import io
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import FileResponse
from reportlab.lib.pagesizes import A4
from django.conf import settings
from reportlab.lib.utils import simpleSplit

import random


#locale.setlocale(locale.LC_ALL, 'uk_UA')


def index(request):
    #відображення питань          
    questions = Question.objects.filter(processed=False).values()
    
    context = {'questions': questions}
    
    return render(request, 'chemistry/index.html', context)

def info(request):
    return render(request, 'chemistry/info.html')

@login_required
def edit_question(request, question_id):
    """редагувати питання."""
    
    question = Question.objects.get(id=question_id)
    #визначення id наступного питання
    def next_question(question_id):
        question_id = question_id + 1 
        if Question.objects.get(id = (question_id)).DoesNotExist:
            #next_question(question_id)
            question_id = question_id + 1 
        else:
            return(question_id)

    if request.method != 'POST':
        form = QuestionForm(instance=question)
    else:
        form = QuestionForm(instance=question, data=request.POST)
        if form.is_valid():
            form.save()
            
            next_q = question_id + 1 #працює перемикання між питаннями
            #next_q = next_question(question_id) #не працює перемикання між питаннями
        
            return redirect('chemistry:edit_question', question_id=next_q)

    context = {'question': question, 'form': form}
    return render(request, 'chemistry/edit_question.html', context)

@login_required
def add_question(request):
    """додати питання."""
    
    if request.method != 'POST':
        form = QuestionForm(initial={'processed':True})
    else:
        form = QuestionForm(data=request.POST)
        if form.is_valid():
            form.save()
            
            return redirect('chemistry:add_question')

    context = {'form': form}
    return render(request, 'chemistry/add_question.html', context)

def generator(request):
    #сторінка для генерації контрольних
    def make_pdf(variants):
        font_path = os.path.join(settings.BASE_DIR, 'chemistry', 'static', 'chemistry', 'font', 'Montserrat-Regular.ttf')  # Шлях до файлу шрифту
        # print("Шлях до шрифту:", font_path)
        # if not os.path.exists(font_path):
        #      raise FileNotFoundError(f"Файл шрифту не знайдено: {font_path}")
        
        pdfmetrics.registerFont(TTFont('Montserrat', font_path))  # Реєструємо шрифт

        buffer = io.BytesIO()
        pdf_canvas = canvas.Canvas(buffer, pagesize=A4)
        pdf_canvas.setFont('Montserrat', 14)
        page_width, page_height = A4  # Розміри сторінки
        left_margin = 50
        right_margin = 50
        max_width = page_width - left_margin - right_margin  # Максимальна ширина тексту
        y_position = page_height - 50  # Початкова позиція для тексту (50 відступ зверху)

        for variant_num, questions in variants.items():
            # pdf_canvas.drawString(left_margin, y_position, f"Варіант {variant_num}")
            y_position -= 20

            for question in questions:
                # Розбиваємо текст, який перевищує ширину сторінки
                wrapped_text = simpleSplit(question, 'Montserrat', 14, max_width)
                
                for line in wrapped_text:
                    pdf_canvas.drawString(left_margin, y_position, line)
                    y_position -= 15

                    # Якщо текст виходить за нижній край сторінки, додаємо нову сторінку
                    if y_position < 50:
                        pdf_canvas.showPage()
                        pdf_canvas.setFont('Montserrat', 14)  # Повторно встановлюємо шрифт для нової сторінки
                        y_position = page_height - 50
        pdf_canvas.save()
        buffer.seek(0)
        return buffer

    def generate(numOfVariants, numOfQuestions, multicategory):
        category_questions = []
        # вибір питань у всіх категоріях
        for category in multicategory:
            print(category)
            cat_questions = (object['text'] for object in Question.objects.filter(category_def = category).values('text'))
            for question in cat_questions:
                category_questions.append(question)
        total_questions = len(category_questions)
        print(total_questions)

        generated_q = {}
        x = 0
        y = 0
        if (numOfQuestions*numOfVariants) <= len(category_questions):
            for x in range(numOfVariants):
                variant = [f'Варіант {x+1}'] #вставлення номера варіанта
                for y in range(numOfQuestions):
                    q = category_questions[random.randint(0, len(category_questions)-1)]
                    variant.append(f'{str(y+1)+". " + q}')
                    print(variant)
                    category_questions.remove(q)
                    y += 1
                generated_q[f'{x+1}'] = variant
                x += 1
        else:
            generated_q = {1:['<span class="material-symbols-rounded"> warning </span>','Недостатня кількість запитань з даної теми в базі, оберіть менше питань або варіантів']}
        return generated_q
    def total_questions(multicategory):
        total_questions = 0
        for category in multicategory:
            total_questions += len(Question.objects.filter(category_def = category))
        return total_questions
    
# Якщо потрібно створити PDF
    if request.method == "POST" and 'generate_pdf' in request.POST:
        variants = request.session.get('generated_variants', {})
        if variants:
            pdf_buffer = make_pdf(variants)
            return FileResponse(pdf_buffer, as_attachment=True, filename="variants.pdf")

 
    generated_q = []
    if request.method == "POST":
        
        form = VariantCreationForm(request.POST) #or None
        
        if form.is_valid():
            numOfVariants = int(request.POST.get('numOfVariants',''))
            numOfQuestions = int(request.POST.get('numOfQuestions',''))
            # category = str(request.POST.get('category','')) для генерації питань з однієї категорії
            multicategory = request.POST.getlist('category')
            generated_q = generate(numOfVariants, numOfQuestions, multicategory)
            total_questions = total_questions(multicategory)
           # Зберігаємо згенеровані варіанти в сесії
            request.session['generated_variants'] = generated_q

    else:
        form = VariantCreationForm()

    
   
    context = {'generated_q': generated_q, 'form': form, 'total_questions': total_questions}
    return render(request, 'chemistry/generator.html', context)
