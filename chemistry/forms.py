from django import forms

from .models import Grade, Section, Category, Question

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['category', 'text', 'level', 'answer', 'grade',  'processed']
        labels = {'topic':'Категорія','text':'Текст', 'level':'Рівень складності', 'answer': 'Відповідь на питання', 'grade': 'Для якого класу',  'processed': 'Опрацьоване?'}

class VariantCreationForm(forms.Form):
    # authors = forms.ModelMultipleChoiceField(queryset=Author.objects.all())
    questions = [question.category_def for question in Question.objects.all()] #вибрати всі теми запитань
    CHOICES = {}
    for item in questions:      
        CHOICES[item] = item
    numOfVariants = forms.IntegerField(widget=forms.NumberInput(attrs={'min':1,'class': 'variants-num', 'placeholder':'Кількість варіантів'}), label = False)
    numOfQuestions = forms.IntegerField(widget=forms.NumberInput(attrs={'min':1,'class': 'questions-num', 'placeholder':'Кількість питань'}), label = False)

    # один вибір
    # category = forms.ChoiceField(choices=CHOICES, widget=forms.Select(attrs={'class': 'category-select'}), label = False) 
    
    # багато виборів через div та checkbox
    category = forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'category-select'}), label=False) 
   
    # багато виборів через select та option
    # category = forms.MultipleChoiceField(choices=CHOICES, widget=forms.SelectMultiple(attrs={'class': 'category-select'}), label=False) 