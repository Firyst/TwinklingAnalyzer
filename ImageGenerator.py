from PIL import Image, ImageDraw
from LogicFunction import *

# Создаем белый квадрат
def graph(func: LogicFunction):
    f=LogicFunction('a+b+c')
    img = Image.new('RGBA', (len(func.get_variables())*100,len(func.get_variables())*100+100), 'white')
    draw = ImageDraw.Draw(img)
    # Рисуем результат функции
    draw_text = ImageDraw.Draw(img)
    draw_text.text((3, 12),'func',fill=('black'))
    for j in range(len(f.generate_boolean_table())):
        string = f.generate_boolean_table()[j]
        if int(string[1]) == 0:
            draw.line((10 + 20 * (j + 1), 20, 10 + 20 * (j + 1) + 20, 20), fill='blue', width=3)
        else:
            draw.line((10 + 20 * (j + 1), 10, 10 + 20 * (j + 1) + 20, 10), fill='blue', width=3)
        for j in range(1, len(f.generate_boolean_table())):
            if f.generate_boolean_table()[j - 1][1] != f.generate_boolean_table()[j][1]:
                draw.line((10 + 20 * (j + 1), 10, 10 + 20 * (j + 1), 20), fill='blue', width=3)
    # Рисуем значения переменных
    for i in range(len(f.get_variables())):
        name=f.get_variables()[i]
        draw_text = ImageDraw.Draw(img)
        draw_text.text((10, i * 20 + 42 ), name, fill=('black'))

    for i in range(len(f.get_variables())):
        for j in range(len(f.generate_boolean_table())):
            string=f.generate_boolean_table()[j]
            line = i * 20 + 10
            if int(string[0][i]) == 0:
                draw.line((10 + 20*(j+1), line + 40, 10 + 20*(j+1) + 20, line + 40), fill='blue', width=3)
            else:
                draw.line((10 + 20*(j+1), line + 30, 10 + 20*(j+1) + 20, line+ 30), fill='blue', width=3)
        for j in range(1,len(f.generate_boolean_table())):
            line = i * 20 + 10
            if f.generate_boolean_table()[j-1][0][i] != f.generate_boolean_table()[j][0][i]:
                draw.line((10 + 20*(j+1), line + 30, 10 + 20*(j+1), line + 40), fill='blue', width=3)


    img.show()

graph(LogicFunction('a+b+c'))