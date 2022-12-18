# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
from LogicFunction import *


def graph(func: LogicFunction, text_color, bg_color, graph_color, output):
    """! Сгенерировать график логической функции и сохранить его.
    @param func: сама логическая функция (объект LogicFunction)
    @param text_color: цвет текста
    @param bg_color: цвет фона
    @param graph_color: цвет самого значения графика
    @param output: файл, в которых сохранять график
    """
    f_vars = func.get_variables()
    gbt = func.generate_boolean_table()  # таблица истинности

    img = Image.new('RGBA', (2 ** len(f_vars) * 90 + 150, len(f_vars) * 100 + 180), bg_color)
    draw = ImageDraw.Draw(img)

    # Загружаем шрифт для подписей
    # Код заимствован из https://www.blog.pythonlibrary.org/2021/02/02/drawing-text-on-images-with-pillow-and-python/
    font = ImageFont.truetype(font="resources/SourceCodePro-Black.ttf", size=40)
    # конец заимствования

    # Рисуем результат функции
    draw_text = ImageDraw.Draw(img)
    draw_text.text((10, 60), 'func', fill=text_color, font=font)
    for j in range(len(gbt)):
        string = gbt[j]
        if int(string[1]) == 0:
            draw.line((40 + 90 * (j + 1), 100, 40 + 90 * (j + 1) + 90, 100), fill=graph_color, width=4)
        else:
            draw.line((40 + 90 * (j + 1), 40, 40 + 90 * (j + 1) + 90, 40), fill=graph_color, width=4)
        for j in range(1, len(gbt)):
            if gbt[j - 1][1] != gbt[j][1]:
                draw.line((40 + 90 * (j + 1), 39, 40 + 90 * (j + 1), 102), fill=graph_color, width=4)

    # Рисуем названия переменных
    for i in range(len(f_vars)):
        name = f_vars[i]
        draw_text = ImageDraw.Draw(img)
        draw_text.text((10, i * 100 + 160), name, fill=text_color, font=font)

    # Рисуем значения переменных
    for i in range(len(f_vars)):
        for j in range(len(gbt)):
            # Горизонтальные линии
            string = gbt[j]
            line = i * 100 + 20
            if int(string[0][i]) == 0:
                draw.line((40 + 90 * (j + 1), line + 180, 40 + 90 * (j + 1) + 90, line + 180),
                          fill=graph_color, width=4)
            else:
                draw.line((40 + 90 * (j + 1), line + 140, 40 + 90 * (j + 1) + 90, line + 140),
                          fill=graph_color, width=4)

        for j in range(1, len(gbt)):
            # Вертикальные линии
            line = i * 100 + 20
            if gbt[j - 1][0][i] != gbt[j][0][i]:
                draw.line((40 + 90 * (j + 1), line + 139, 40 + 90 * (j + 1), line + 182), fill=graph_color, width=4)

    # Сохраняем результат
    img.save(output, 'png')
