import datetime
import openpyxl
from openpyxl.styles import Font, Alignment, NamedStyle, Border, Side
from io import BytesIO
from django.core.files import File
from django.db.models import QuerySet
from django.db import models
from users.models import User
from telegram import Update
from telegram.ext import CallbackContext
from utils.models import CreateTracker, datetime_str
from typing import Tuple



class Question(CreateTracker):
    msg_id = models.BigAutoField(primary_key=True, verbose_name="Номер сообщения")  # telegram_id
    user = models.ForeignKey(User, verbose_name='Отправитель', on_delete=models.DO_NOTHING)
    text = models.TextField(verbose_name='Вопрос')

    def __str__(self):
        return f'msg {self.msg_id} from {self.user}'


    @classmethod
    def add_question(cls, update: Update, context: CallbackContext):
        user, created = User.get_user_and_created(update=update, context=context)
        new_question, created = cls.objects.update_or_create(
            msg_id=update.message.message_id,
            user=user,
            text=update.message.text
        )
        return new_question, created
    
    def generate_excel_file_name(queryset: QuerySet):
        count = str(queryset.count())
        first_date, last_date = datetime_str(queryset.first().created_at), datetime_str(queryset.last().created_at)
        if count.endswith('1'):
            question_numerals = 'вопрос'
        elif count.endswith(('2','3','4',)):
            question_numerals = 'вопроса'
        else:
            question_numerals = 'вопросов'
        excel_file_name = f"{count} {question_numerals} заданных с {first_date} по {last_date} по Москве"
        return excel_file_name


    @classmethod
    def export_question_to_excel(cls) -> Tuple[str, File]:
        questions = cls.objects.all()
        
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = cls.generate_excel_file_name(questions)
           
        # Определение стилей
        bold_font = Font(bold=True)
        centered_alignment = Alignment(horizontal='center', vertical='center')
        thin_border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin")
        )

         # Заголовки таблицы
        headers = [
            'Номер сообщения', 'Отправитель', '', '', 'Вопрос', 'Задан'
        ]

        for col_num, header in enumerate(headers, 1):
            cell = worksheet.cell(row=1, column=col_num)
            cell.value = header
            cell.font = bold_font
            cell.alignment = centered_alignment
            cell.border = thin_border


        sender_headers = ['@никнейм', 'имя', 'фамилия']
        for col_num, header in enumerate(sender_headers, 2):
            cell = worksheet.cell(row=2, column=col_num)
            cell.value = header
            cell.font = bold_font
            cell.alignment = centered_alignment
            cell.border = thin_border

        # Объединение ячеек для двухуровневого заголовка
        worksheet.merge_cells(start_row=1, start_column=2, end_row=1, end_column=4)
        worksheet.merge_cells(start_row=1, start_column=1, end_row=2, end_column=1)
        worksheet.merge_cells(start_row=1, start_column=5, end_row=2, end_column=5)
        worksheet.merge_cells(start_row=1, start_column=6, end_row=2, end_column=6)

        # Заполнение данными
        for row_num, question in enumerate(questions, 3):
            # Номер сообщения
            cell = worksheet.cell(row=row_num, column=1)
            cell.value = question.msg_id
            cell.alignment = centered_alignment
            cell.border = thin_border


            # Отправитель
            sender_values = [
                f"@{str(question.user.username)}",
                str(question.user.first_name),
                str(question.user.last_name),
            ]
            for col_num, value in enumerate(sender_values, 2):
                cell = worksheet.cell(row=row_num, column=col_num)
                cell.value = value
                cell.alignment = centered_alignment
                cell.border = thin_border

            # Вопрос
            cell = worksheet.cell(row=row_num, column=5)
            cell.value = question.text
            cell.border = thin_border

            # Дата и время
            cell = worksheet.cell(row=row_num, column=6)
            cell.value = f"{datetime_str(question.created_at)} по Москве"
            cell.alignment = centered_alignment
            cell.border = thin_border

        # Автоматическое изменение ширины столбцов
        for col_index, column_cells in enumerate(worksheet.columns):
            non_merged_cells = [cell for cell in column_cells if not isinstance(cell, openpyxl.cell.MergedCell)]
            if not non_merged_cells:
                continue
            length = max(len(str(cell.value)) for cell in non_merged_cells)
            worksheet.column_dimensions[non_merged_cells[0].column_letter].width = length

        excel_file = BytesIO()
        workbook.save(excel_file)
        excel_file.seek(0)          
        return f"{worksheet.title}.xlsx", excel_file 