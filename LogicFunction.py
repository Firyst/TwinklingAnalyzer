# -*- coding: utf-8 -*-

from itertools import product
from string import punctuation, ascii_letters, digits, ascii_lowercase

# словарь замен для представления функции в стандартном python виде
REPLACES = {' and ': ['&&', '*', ' и ', ' AND ', ' И ', '&', '⋀'],
            ' or ': ['||', '+', ' или ', ' OR ', ' ИЛИ ', '|', '⋁'],
            ' not ': ['!', 'NOT ', 'не ', 'НЕ ', 'not ', '¬'],
            ' ^ ': [' xor ', ' XOR ', '==', " ⊕ "]}
# строка с корректными символами
VALID_SYMBOLS = ascii_letters + "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя" + "()^ " + digits


class InputException(Exception):
    """! Кастомное исключение
    """
    pass


class LogicFunction:
    """! Класс, описывающий логическое выражение
    """

    def __init__(self, expression: str):
        """! Инициализация выражения
        @param expression  выражения в указанном формате
        """

        self.exp = expression

        # замена возможных записей функции на python-интерпретируемые
        for repl_symbol in REPLACES:
            for possible_entry in REPLACES[repl_symbol]:
                self.exp = self.exp.replace(possible_entry, repl_symbol)

        # чистим лишние пробелы
        while '  ' in self.exp:
            self.exp = self.exp.replace('  ', ' ')

        self.exp = self.exp.replace("( not", "(not")  # чтобы выгядело аккуратнее

        # проверяем на корректность символов
        for symb in self.exp:
            if symb not in VALID_SYMBOLS:
                raise InputException(f"Неизвестный символ: '{symb}'")

        # проверяем количество переменных
        variables = self.get_variables()

        if len(variables) < 2:
            raise InputException("В функции должно быть хотя бы две переменных.")

        for variable in self.get_variables():
            if variable[0] in digits:
                raise InputException("Переменные не могут начинаться с цифр.")
            if len(variable) > 4:
                raise InputException("Названия переменных должны быть короче 5 символов.")

        # проверяем корректность скобочек
        # ошибка вызовется внутри функции
        test_value = self.get_result((0,) * len(variables))

    def get_variables(self):
        """! Получить названия всех переменных в функции
        @return отсортированный list названий переменных
        """
        variables_left = self.exp
        for replacing_symbol in punctuation:
            # замена скобок
            variables_left = variables_left.replace(replacing_symbol, ' ')

        for operand in REPLACES.keys():
            # операнды - это не переменные, их заменяем
            variables_left = variables_left.replace(operand, ' ')
        return sorted(list(set(variables_left.split())))

    def get_result(self, values) -> int:
        """! Выполнить функцию с определенными значениями переменных.
        @param values  Итерируемый объект из 1 и 0. Переменные подаются в таком же порядке,
            в котором они возвращаются функцией get_variables()
        @return результат функции при заданных входных данных
        """
        eval_string = ''
        for i, var in enumerate(self.get_variables()):
            eval_string += f"{var} = {values[i]}\n"
        eval_string += 'res = ' + self.exp
        res = {}
        try:
            exec(eval_string, globals(), res)
        except SyntaxError:
            raise InputException("Некорректная функция. Проверьте парность скобок и операторов.")
        return int(res["res"])

    def generate_boolean_table(self) -> list:
        """! Генерирует таблицу истинности для логической функции
        @return  list of tuples ((tuple: input_values), result)
        """
        func_vars = self.get_variables()  # get all variables
        result = []
        for func_case in product((0, 1), repeat=len(func_vars)):
            case_result = self.get_result(func_case)
            result.append((func_case, case_result))
        return result

    def simplify_sdnf(self):
        """Упрощение методом Квайна СДНФ
        @return объект LogicFunction с упрощенной функцией
        """
        array = self.generate_boolean_table()
        cur_names = self.get_variables()
        # входной список с котежами
        array_one = []
        # создаем список переменных, которые дают 1 в результате
        for i in range(len(array)):
            if array[i][1] == 1:
                array_one.append(array[i][0])
        if len(array_one) == 0:
            raise InputException("Функция всегда является константой 0")
        # создаем cписок, где распределяем по количеству единиц
        array_of_one = dict()
        for line in array_one:
            line_list = list(line)
            count_1 = line_list.count(1)
            if count_1 in array_of_one:
                array_of_one[count_1].append(line)
            else:
                array_of_one[count_1] = [line]
        # склеиваем комбинации между соседними группами,заменяем различные символы на Х, где ключ - позиция Х
        array_glue = dict()
        for key1 in array_of_one.keys():
            for key2 in array_of_one.keys():
                a = array_of_one.get(key1)
                b = array_of_one.get(key2)
                for x in range(len(a)):
                    for y in range(len(b)):
                        kol = 0
                        for z in range(len(a[x])):
                            if a[x][z] == b[y][z]:
                                kol += 1
                            else:
                                dif = z + 1
                        if kol == len(a[x]) - 1:
                            different = tuple(''.join(map(str, a[x][:dif - 1])) + 'X' + ''.join(map(str, a[x][dif:])))
                            if dif in array_glue:
                                array_glue[dif].append(different)
                            else:
                                array_glue[dif] = [different]
        # проверка, что упрощение возможно
        sdnf = []
        for key in array_of_one.keys():
            a = array_of_one.get(key)
            for i in a:
                term = []
                for j in range(len(i)):
                    if i[j] == 1:
                        term.append(cur_names[j])
                    else:
                        term.append('!' + cur_names[j])
                sdnf.append('*'.join(term))
        # склеиваем комбинации внутри группы,заменяем различные символы на Х, где ключ - позиция Х
        for key in array_glue.keys():
            a = array_glue.get(key)
            a = list(a)
            for i in range(len(a) - 1):
                kol = 0
                for j in range(len(a[i])):
                    if a[i][j] == a[i + 1][j]:
                        kol += 1
                    else:
                        dif = j + 1
                if kol == len(a[i]) - 1:
                    different = tuple(''.join(map(str, a[i][:dif - 1])) + 'X' + ''.join(map(str, a[i][dif:])))
                    array_glue[key].append(different)
                    array_glue[key].remove(a[i])
                    array_glue[key].remove(a[i + 1])
        # создаем словарь, где ключи - полученные склеенные выражения
        final_table = dict()
        for key in array_glue.keys():
            a = array_glue.get(key)
            for imp in a:
                if imp in final_table:
                    pass
                else:
                    final_table[imp] = []
        # в словарь добавляем первоначальные импликанты
        for i in range(len(array_one)):
            for key in final_table:
                kol = key.count('X')
                for j in range(len(array_one[i])):
                    if str(array_one[i][j]) == key[j]:
                        kol += 1
                if kol == len(array_one[i]):
                    final_table[key].append(array_one[i])
        # составляем МДНФ
        mdnf = []
        for key in final_table.keys():
            a = final_table.get(key)
            count_X = key.count('X')
            if count_X == len(key):
                return 1
            if len(a) != 0:
                term = []
                for j in range(len(key)):
                    if key[j] != 'X':
                        if key[j] == '1':
                            term.append(cur_names[j])
                        else:
                            term.append('!' + cur_names[j])
                mdnf.append('*'.join(term))
            for key1 in final_table.keys():
                if key1 != key:
                    b = final_table.get(key1)
                    for i in a:
                        for j in b:
                            if i == j:
                                final_table[key1].remove(j)
        if mdnf:
            return LogicFunction('+'.join(mdnf))
        return LogicFunction('+'.join(sdnf))

    def simplify_sknf(self):
        """Упрощение методом Квайна СКНФ
        @return объект LogicFunction с упрощенной функцией
        """
        array = self.generate_boolean_table()
        cur_names = self.get_variables()
        # входной список с котежами
        array_zero = []
        # создаем список переменных, которые дают 0 в результате
        for i in range(len(array)):
            if array[i][1] == 0:
                array_zero.append(array[i][0])
        if len(array_zero) == 0:
            raise InputException("Функция всегда является константой 1")
        # создаем cписок, где распределяем по количеству нулей
        array_of_zero = dict()
        for line in array_zero:
            line_list = list(line)
            count_0 = line_list.count(0)
            if count_0 in array_of_zero:
                array_of_zero[count_0].append(line)
            else:
                array_of_zero[count_0] = [line]
        # склеиваем комбинации между соседними группами,заменяем различные символы на Х, где ключ - позиция Х
        array_glue = dict()
        for key1 in array_of_zero.keys():
            for key2 in array_of_zero.keys():
                a = array_of_zero.get(key1)
                b = array_of_zero.get(key2)
                for x in range(len(a)):
                    for y in range(len(b)):
                        kol = 0
                        for z in range(len(a[x])):
                            if a[x][z] == b[y][z]:
                                kol += 1
                            else:
                                dif = z + 1
                        if kol == len(a[x]) - 1:
                            different = tuple(''.join(map(str, a[x][:dif - 1])) + 'X' + ''.join(map(str, a[x][dif:])))
                            if dif in array_glue:
                                array_glue[dif].append(different)
                            else:
                                array_glue[dif] = [different]
        # проверка, что упрощение возможно
        sknf = []
        for key in array_of_zero.keys():
            a = array_of_zero.get(key)
            for i in a:
                term = []
                for j in range(len(i)):
                    if i[j] == 0:
                        term.append(cur_names[j])
                    else:
                        term.append('!' + cur_names[j])
                sknf.append('(' + '+'.join(term) + ')')
        # склеиваем комбинации внутри группы,заменяем различные символы на Х, где ключ - позиция Х
        for key in array_glue.keys():
            a = array_glue.get(key)
            a = list(a)
            for i in range(len(a) - 1):
                kol = 0
                for j in range(len(a[i])):
                    if a[i][j] == a[i + 1][j]:
                        kol += 1
                    else:
                        dif = j + 1
                if kol == len(a[i]) - 1:
                    different = tuple(''.join(map(str, a[i][:dif - 1])) + 'X' + ''.join(map(str, a[i][dif:])))
                    array_glue[key].append(different)
                    array_glue[key].remove(a[i])
                    array_glue[key].remove(a[i + 1])
        # создаем словарь, где ключи - полученные склеенные выражения
        final_table = dict()
        for key in array_glue.keys():
            a = array_glue.get(key)
            for imp in a:
                if imp in final_table:
                    pass
                else:
                    final_table[imp] = []
        # в словарь добавляем первоначальные импликанты
        for i in range(len(array_zero)):
            for key in final_table:
                kol = key.count('X')
                for j in range(len(array_zero[i])):
                    if str(array_zero[i][j]) == key[j]:
                        kol += 1
                if kol == len(array_zero[i]):
                    final_table[key].append(array_zero[i])
        # составляем МКНФ
        mknf = []
        for key in final_table.keys():
            a = final_table.get(key)
            count_X = key.count('X')
            if count_X == len(key):
                return 0
            if len(a) != 0:
                term = []
                for j in range(len(key)):
                    if key[j] != 'X':
                        if key[j] == '0':
                            term.append(cur_names[j])
                        else:
                            term.append('!' + cur_names[j])
                mknf.append('(' + '+'.join(term) + ')')
            for key1 in final_table.keys():
                if key1 != key:
                    b = final_table.get(key1)
                    for i in a:
                        for j in b:
                            if i == j:
                                final_table[key1].remove(j)
        if mknf:
            return LogicFunction('*'.join(mknf))
        return LogicFunction('*'.join(sknf))


def generate_function_from_table(table: list, method=0, var_names=ascii_lowercase) -> LogicFunction:
    """! Генерирует и возвращает объект LogicFunction по таблице истинности формата:
    list: [((tuple: input_values), result)]
    Используемые названия переменных: a, b, c, d...
    @param table list: [((tuple: input_values), result)]
    @param method 0 - СДНФ, 1 - СКНФ
    @param var_names: итерируемый объект с названиями переменных. По умолчанию маленьий латинский алфавит.
    @return: объект LogicFunction с совершенной формой
    """
    snf = []  # список с логическими выражениями
    for line in table:
        term = []  # список одного логического выражения
        if line[1] == method:
            for j in range(len(line[0])):
                if line[0][j] == 1 and method == 1:
                    term.append(var_names[j])
                elif line[0][j] == 0 and method == 1:
                    term.append('!' + var_names[j])
                elif line[0][j] == 0 and method == 0:
                    term.append(var_names[j])
                elif line[0][j] == 1 and method == 0:
                    term.append('!' + var_names[j])
        else:
            continue
        if method == 1:
            snf.append('*'.join(term))
        else:
            snf.append('(' + '+'.join(term) + ')')
    if method == 1:
        return LogicFunction('+'.join(snf))
    return LogicFunction('*'.join(snf))
