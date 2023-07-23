from customtkinter import *
from PIL import Image
from re import match
from localization import txt
import sys
import os


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# Глобальные переменные, отвечающие за текущее состояние приложения

cur_lang = 'rus'
cur_error_m = 0
cur_error_h = 0
cur_result = -1
min_best_weight = 0
max_best_weight = 0
instruction = None

# Минимальные и максимальные значения ИМТ и цвета, соответствующие вариантам интерпретации

results = [(-1, 16), (16, 18.5), (18.5, 25), (25, 30), (30, 35), (35, 40), (40, 1e11)]
results_colors = ['#E60000', '#FFB800', '#00E600', '#FFB800', '#E60000', '#E60000', '#E60000', 'black']


# Проверка на корректность данных в поле ввода

def is_valid(new_value):
    if new_value == '':
        return True
    return match("^0$|^0\.\\d?$|^[0-9]+\.?\\d?$", new_value) is not None and len(new_value) <= 5


# Определение интерпретации, соответствующей данному значению ИМТ

def find_result(bmi):
    global cur_result
    for idx in range(len(results)):
        if results[idx][0] < bmi <= results[idx][1]:
            cur_result = idx
            return txt[f'result{idx}'][cur_lang]


# Изменение языка

def set_language(language):
    global cur_lang
    cur_lang = language
    label_result.configure(text=txt[f'result{cur_result}'][cur_lang])
    label_error_mass.configure(text=txt[f'error{cur_error_m}'][cur_lang])
    label_error_height.configure(text=txt[f'error{cur_error_h}'][cur_lang])
    window.title(txt['window-title'][cur_lang])
    label_input_mass.configure(text=txt['input-mass'][cur_lang])
    label_input_height.configure(text=txt['input-height'][cur_lang])
    button_calculate.configure(text=txt['calc'][cur_lang])
    label_index.configure(text=txt['index'][cur_lang])
    label_kg.configure(text=txt['kg'][cur_lang])
    label_cm.configure(text=txt['cm'][cur_lang])
    label_your_best_weight.configure(
        text=f'{txt["best-weight"][cur_lang]} {min_best_weight} - {max_best_weight} {txt["kg"][cur_lang]}'
    )
    return


# События, привязанные к кнопкам смены языка

def rus_button_event():
    set_language('rus')


def eng_button_event():
    set_language('eng')


# Проверки на корректность данных в полях ввода при нажатии кнопки Рассчитать, определение и запись номера ошибки

def check_mass(mass):
    global cur_error_m
    if mass == '':
        cur_error_m = 1
    elif mass[-1] == '.':
        cur_error_m = 2
    elif mass[:2] == '00':
        cur_error_m = 4
    else:
        cur_error_m = 0
        return True
    return False


def check_height(height):
    global cur_error_h
    if height == '':
        cur_error_h = 1
    elif height[:2] == '00':
        cur_error_h = 4
    elif height[-1] == '.':
        cur_error_h = 2
    elif height == '0':
        cur_error_h = 3
    else:
        cur_error_h = 0
        return True
    return False


def check_entries():
    (a, b) = (check_mass(entry_mass.get()), check_height(entry_height.get()))
    label_error_height.configure(text=txt[f'error{cur_error_h}'][cur_lang])
    label_error_mass.configure(text=txt[f'error{cur_error_m}'][cur_lang])
    return a and b


# Расчёт идеального веса для данного роста

def calculate_best_weight(height):
    _min = round(18.51 * height * height, 2)
    _max = round(25 * height * height, 2)
    return _min, _max


# Рассчёт по формуле и вывод ИМТ

def calculate():
    global min_best_weight, max_best_weight
    if not check_entries():
        return
    mass = float(entry_mass.get())
    height = float(entry_height.get()) / 100
    bmi = round(mass / (height * height), 4)
    new_result = find_result(bmi)
    label_result.configure(
        text=new_result,
        text_color=results_colors[cur_result]
    )
    bmi = str(round(bmi, 2))
    if len(bmi) == 1:
        bmi += ',00'
    elif bmi[-2] == '.':
        bmi += '0'
    bmi = bmi[:-3] + ',' + bmi[-2:]
    label_bmi.configure(text=bmi)
    (min_best_weight, max_best_weight) = calculate_best_weight(height)
    label_your_best_weight.configure(
        text=f'{txt["best-weight"][cur_lang]} {min_best_weight} - {max_best_weight} {txt["kg"][cur_lang]}'
    )


# Вызов и настройка основного окна

set_appearance_mode("light")
window = CTk()
window.title(txt['window-title'][cur_lang])
window.iconbitmap(resource_path('ico.ico'))

# Параметры сетки окна

min_sizes = (48, 35, 48, 35, 220, 40, 75, 35, 40, 35)
weights = (1, 0, 1, 0, 1, 0, 1, 1, 1, 0)
for i in range(10):
    window.rowconfigure(i, minsize=min_sizes[i], weight=weights[i])
min_sizes = (33, 240, 180, 45, 45)
weights = (0, 4, 3, 0, 0)
for i in range(5):
    window.columnconfigure(i, minsize=min_sizes[i], weight=weights[i])

# Размещение элементов интерфейса основного окна

label_input_mass = CTkLabel(master=window, font=('Helvetica', 18), text=txt['input-mass'][cur_lang])
label_input_mass.grid(row=0, column=1, sticky='sw')
label_kg = CTkLabel(master=window, text=txt['kg'][cur_lang], padx=15, font=('Helvetica', 18))
label_kg.grid(row=1, column=2, sticky='w')
mass_ico = CTkImage(light_image=Image.open(resource_path('mass.png')), size=(20, 20))
label_mass_ico = CTkLabel(master=window, text='', image=mass_ico)
label_mass_ico.grid(row=0, column=0, sticky='s')

label_input_height = CTkLabel(master=window, font=('Helvetica', 18), text=txt['input-height'][cur_lang])
label_input_height.grid(row=2, column=1, sticky='sw')
label_cm = CTkLabel(master=window, text=txt['cm'][cur_lang], padx=15, font=('Helvetica', 18))
label_cm.grid(row=3, column=2, sticky='w')
height_ico = CTkImage(light_image=Image.open(resource_path('height.png')), size=(24, 24))
label_height_ico = CTkLabel(master=window, text='', image=height_ico)
label_height_ico.grid(row=2, column=0, sticky='s')

input_validation = (window.register(is_valid), "%P") # Регистрация функции для валидации поля ввода
entry_mass = CTkEntry(master=window, validate='key', validatecommand=input_validation)
entry_mass.grid(row=1, column=1, sticky='we')
entry_height = CTkEntry(master=window, validate='key', validatecommand=input_validation)
entry_height.grid(row=3, column=1, sticky='we')

label_error_mass = CTkLabel(master=window, text=' ', text_color='#E60000')
label_error_mass.grid(row=0, column=2, columnspan=3, sticky='sw')
label_error_height = CTkLabel(master=window, text=' ', text_color='#E60000')
label_error_height.grid(row=2, column=2, columnspan=3, sticky='sw')

button_calculate = CTkButton(
    master=window, text=txt['calc'][cur_lang], font=('Helvetica', 32), command=calculate, height=90, width=300
)
button_calculate.grid(row=4, column=0, columnspan=5)

label_index = CTkLabel(master=window, text=txt['index'][cur_lang], font=('Helvetica', 28))
label_index.grid(row=5, column=0, columnspan=5, sticky='s')

label_bmi = CTkLabel(master=window, text='XX,XX', font=('Helvetica', 54))
label_bmi.grid(row=6, column=0, columnspan=5)

label_result = CTkLabel(master=window, text=txt['result-1'][cur_lang], font=('Helvetica', 16))
label_result.grid(row=7, column=0, columnspan=5, sticky='n')

label_your_best_weight = CTkLabel(master=window, text=txt['best-weight'][cur_lang], font=('Helvetica', 14))
label_your_best_weight.grid(row=8, column=0, columnspan=5, sticky='n')

label_choose_language = CTkLabel(master=window, text='Выберите язык / Choose Language \N{RIGHTWARDS ARROW}', padx=5)
label_choose_language.grid(row=9, column=1, columnspan=2, sticky='e')

flag_ru = CTkImage(light_image=Image.open(resource_path('ru.png')), size=(24, 16))
button_rus = CTkButton(master=window, text='', command=rus_button_event, width=35, height=25, image=flag_ru)
button_rus.grid(row=9, column=3)
flag_en = CTkImage(light_image=Image.open(resource_path('en.png')), size=(24, 16))
button_eng = CTkButton(master=window, text='', command=eng_button_event, width=35, height=25, image=flag_en)
button_eng.grid(row=9, column=4, padx=1)

window.mainloop() # Запуск цикла событий
