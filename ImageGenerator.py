from PIL import Image, ImageDraw
from LogicFunction import *

# Создаем белый квадрат
def graph(func: LogicFunction):
    img = Image.new('RGBA', (2 ** len(func.get_variables())*100,len(func.get_variables())*200+200), 'white')
    draw = ImageDraw.Draw(img)

    '''idraw.rectangle((10, 10, 100, 100), fill='black')'''
    # Рисуем синий прямоугольник с белой оконтовкой.
    draw.rectangle((200, 10, 400, 12), fill='blue', outline=(255, 255, 255))
    draw.rectangle((400, 10, 800, 12), fill='blue', outline=(255, 255, 255))


    img.show()


graph(LogicFunction('a+b+c+d'))