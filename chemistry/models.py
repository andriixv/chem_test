from django.db import models

#Класи(навчальні)
class Grade(models.Model):
    grade = models.IntegerField()
    def __str__(self):
        return f'{self.grade}'

#Розділи
class Section(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    section_name = models.CharField(max_length=50)
    class Meta:
        verbose_name_plural = 'sections'
    def __str__(self):
        return self.section_name
    
#Категорії
class Category(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, default=0)
    category_name = models.CharField(max_length=50)
    class Meta:
        verbose_name_plural = 'categories'
    def __str__(self):
        return self.category_name
    
#Питання
class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=31)
    category_def = models.TextField(default='0')
    text = models.TextField(default='0')
    level = models.IntegerField(default=1)
    answer = models.CharField(max_length=50, default='Немає відповіді')
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, default=6)
    processed = models.BooleanField(default=False)
    # type = models.ForeignKey(Type, on_delete=models.CASCADE)

    def __str__(self):
        return self.text[:100]