from PIL import Image, ImageDraw
from LogicFunction import *

# Создаем белый квадрат
def graph(func: LogicFunction):
    img = Image.new('RGBA', (2 ** len(func.get_variables())*100,len(func.get_variables())*100+100), 'white')
    draw = ImageDraw.Draw(img)
    gbt=func.generate_boolean_table()
    # Рисуем результат функции
    draw_text = ImageDraw.Draw(img)
    draw_text.text((3, 20),'func',fill=('black'))
    for j in range(len(gbt)):
        string = gbt[j]
        if int(string[1]) == 0:
            draw.line((10 + 45 * (j + 1), 50, 10 + 45 * (j + 1) + 45, 50), fill='blue', width=4)
        else:
            draw.line((10 + 45 * (j + 1), 20, 10 + 45 * (j + 1) + 45, 20), fill='blue', width=4)
        for j in range(1, len(gbt)):
            if gbt[j - 1][1] != gbt[j][1]:
                draw.line((10 + 45 * (j + 1), 20, 10 + 45 * (j + 1), 50), fill='blue', width=4)
    # Рисуем значения переменных
    for i in range(len(func.get_variables())):
        name=func.get_variables()[i]
        draw_text = ImageDraw.Draw(img)
        draw_text.text((10, i * 50 + 90), name, fill=('black'))

    for i in range(len(func.get_variables())):
        for j in range(len(gbt)):
            string=gbt[j]
            line = i * 50 + 10
            if int(string[0][i]) == 0:
                draw.line((10 + 45*(j+1), line + 90, 10 + 45*(j+1) + 45, line + 90), fill='blue', width=4)
            else:
                draw.line((10 + 45*(j+1), line + 70, 10 + 45*(j+1) + 45, line + 70), fill='blue', width=4)
        for j in range(1,len(gbt)):
            line = i * 50 + 10
            if gbt[j-1][0][i] != gbt[j][0][i]:
                draw.line((10 + 45*(j+1), line + 70, 10 + 45*(j+1), line + 90), fill='blue', width=4)

    img.show()

graph(LogicFunction('!a+b'))