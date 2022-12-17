from PIL import Image, ImageDraw, ImageFont
from LogicFunction import *


def graph(func: LogicFunction, text_color, bg_color, graph_color, output):
    f_vars = func.get_variables()
    img = Image.new('RGBA', (2 ** len(f_vars) * 90 + 150, len(f_vars) * 100 + 180), bg_color)
    draw = ImageDraw.Draw(img)
    gbt = func.generate_boolean_table()

    font = ImageFont.truetype("resources/SourceCodePro-Black.ttf", 40)

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
                draw.line((40 + 90 * (j + 1), 40, 40 + 90 * (j + 1), 100), fill=graph_color, width=4)
    # Рисуем значения переменных
    for i in range(len(f_vars)):
        name = f_vars[i]
        draw_text = ImageDraw.Draw(img)
        draw_text.text((10, i * 100 + 160), name, fill=text_color, font=font)

    for i in range(len(f_vars)):
        for j in range(len(gbt)):
            string = gbt[j]
            line = i * 100 + 20
            if int(string[0][i]) == 0:
                draw.line((40 + 90 * (j + 1), line + 180, 40 + 90 * (j + 1) + 90, line + 180),
                          fill=graph_color, width=4)
            else:
                draw.line((40 + 90 * (j + 1), line + 140, 40 + 90 * (j + 1) + 90, line + 140),
                          fill=graph_color, width=4)
        for j in range(1, len(gbt)):
            line = i * 100 + 20
            if gbt[j - 1][0][i] != gbt[j][0][i]:
                draw.line((40 + 90 * (j + 1), line + 140, 40 + 90 * (j + 1), line + 180), fill=graph_color, width=4)

    img.save(output, 'png')


# graph(LogicFunction('a+!b+c'))
