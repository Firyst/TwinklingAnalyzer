from itertools import product
from string import punctuation, ascii_letters, digits
from string import ascii_lowercase as var_names


# словарь замен для представления функции в стандартном python виде
REPLACES = {' and ': ['&&', '*', ' и ', ' AND ', ' И ', '&', '⋀'],
            ' or ': ['||', '+', ' или ', ' OR ', ' ИЛИ ', '|', '⋁'],
            ' not ': ['!', ' NOT ', ' не ', ' НЕ '],
            ' ^ ': [' xor ', ' XOR ', '==']}
# строка с корректными символами
VALID_SYMBOLS = ascii_letters + "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя" + "()^ " + digits
# print(VALID_SYMBOLS)


class InputException(Exception):
    pass


class LogicFunction:
    """
    Класс, описывающий логическое выражение.
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

        # проверяем на корректность символов
        for symb in self.exp:
            if symb not in VALID_SYMBOLS:
                raise InputException(f"Неизвестный символ: '{symb}'")

        # проверяем количество переменных
        variables = self.get_variables()

        if not len(variables):
            raise InputException("В функции нету ни одной переменной.")

        for variable in self.get_variables():
            if variable in digits:
                raise InputException("Переменные нельзя называть цифрами")

        # проверяем корректность скобочек
        # ошибка вызовется внутри функции
        test_value = self.get_result((0, ) * len(variables))


    def get_current_expression(self) -> str:
        """! Получить текущую запись логической функции.
        @return строка, отображающая логическую функцию с python-совместимыми операторами
        """
        return self.exp

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
            # eval_string.replace(var, str(values[i]))  # has a bad case that should be fixed
        eval_string += 'res = ' + self.exp
        res = {}
        exec(eval_string, globals(), res)
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

    def beautiful_boolean_table(self):
        """! Генерирует визуализацию таблицы истинности для print.
        @return отформатированная строка
        """
        table = self.generate_boolean_table()
        result = '\t'.join(self.get_variables() + ['func'])
        for case in table:
            result += '\n' + '\t'.join(map(str, case[0])) + f"\t{str(case[1])}"
        return result

    def generate_pdnfs(self):
        """PDNF (perfect disjunctive normal form), или СДНФ.
        Returns: объект LogicFunction в СДНФ

        """
        pass

    def generate_pcnfs(self):
        """PCNF (perfect conjunctive normal form), или СКНФ.
        Returns: объект LogicFunction в СКНФ

        """
        pass

    def simplify_sdnf(self):
        """Упрощение методом Квайна СДНФ
        Returns: объект LogicFunction с упрощенной функцией

        """
        mas = self.generate_boolean_table()
        cur_names = self.get_variables()
        # входной список с котежами
        mas_one = []
        # создаем список переменных, которые дают 1 в результате
        for i in range(len(mas)):
            if mas[i][1] == 1:
                mas_one.append(mas[i][0])
        if len(mas_one) == 0:
            return 0
        # создаем cписок, где распределяем по количеству единиц
        mas_of_one = dict()
        for line in mas_one:
            line_list = list(line)
            count_1 = line_list.count(1)
            if count_1 in mas_of_one:
                mas_of_one[count_1].append(line)
            else:
                mas_of_one[count_1] = [line]
        # склеиваем комбинации между соседними группами,заменяем различные символы на Х, где ключ - позиция Х
        mas_glue = dict()
        for key1 in mas_of_one.keys():
            for key2 in mas_of_one.keys():
                a = mas_of_one.get(key1)
                b = mas_of_one.get(key2)
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
                            if dif in mas_glue:
                                mas_glue[dif].add(different)
                            else:
                                mas_glue[dif] = {different}
        # склеиваем комбинации внутри группы,заменяем различные символы на Х, где ключ - позиция Х
        for key in mas_glue.keys():
            a = mas_glue.get(key)
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
                    mas_glue[key].add(different)
                    mas_glue[key].remove(a[i])
                    mas_glue[key].remove(a[i + 1])
        # создаем словарь, где ключи - полученные склеенные выражения
        final_table = dict()
        for key in mas_glue.keys():
            a = mas_glue.get(key)
            for imp in a:
                if imp in final_table:
                    pass
                else:
                    final_table[imp] = []
        # в словарь добавляем первоначальные импликанты
        for i in range(len(mas_one)):
            for key in final_table:
                kol = key.count('X')
                for j in range(len(mas_one[i])):
                    if str(mas_one[i][j]) == key[j]:
                        kol += 1
                if kol == len(mas_one[i]):
                    final_table[key].append(mas_one[i])
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
        return LogicFunction('+'.join(mdnf))

    def simplify_sknf(self):
        """Упрощение методом Квайна СКНФ
        Returns: объект LogicFunction с упрощенной функцией

        """
        mas = self.generate_boolean_table()
        cur_names = self.get_variables()
        # входной список с котежами
        mas_zero = []
        # создаем список переменных, которые дают 1 в результате
        for i in range(len(mas)):
            if mas[i][1] == 0:
                mas_zero.append(mas[i][0])
        if len(mas_zero)==0:
            return 1
        # создаем cписок, где распределяем по количеству нулей
        mas_of_zero = dict()
        for line in mas_zero:
            line_list = list(line)
            count_0 = line_list.count(1)
            if count_0 in mas_of_zero:
                mas_of_zero[count_0].append(line)
            else:
                mas_of_zero[count_0]=[line]
        # склеиваем комбинации между соседними группами,заменяем различные символы на Х, где ключ - позиция Х
        mas_glue=dict()
        for key1 in mas_of_zero.keys():
            for key2 in mas_of_zero.keys():
                a=mas_of_zero.get(key1)
                b=mas_of_zero.get(key2)
                for x in range(len(a)):
                    for y in range(len(b)):
                        kol = 0
                        for z in range(len(a[x])):
                            if a[x][z] == b[y][z]:
                                kol += 1
                            else:
                                dif = z + 1
                        if kol == len(a[x])-1:
                            different = tuple(''.join(map(str, a[x][:dif-1])) + 'X' + ''.join(map(str, a[x][dif:])))
                            if dif in mas_glue:
                                mas_glue[dif].add(different)
                            else:
                                mas_glue[dif]= {different}
        # склеиваем комбинации внутри группы,заменяем различные символы на Х, где ключ - позиция Х
        for key in mas_glue.keys():
            a=mas_glue.get(key)
            a=list(a)
            for i in range(len(a)-1):
                kol=0
                for j in range(len(a[i])):
                    if a[i][j]==a[i+1][j]:
                        kol+=1
                    else:
                        dif=j+1
                if kol==len(a[i])-1:
                    different = tuple(''.join(map(str, a[i][:dif - 1])) + 'X' + ''.join(map(str, a[i][dif:])))
                    mas_glue[key].add(different)
                    mas_glue[key].remove(a[i])
                    mas_glue[key].remove(a[i+1])
        #создаем словарь, где ключи - полученные склеенные выражения
        final_table=dict()
        for key in mas_glue.keys():
            a=mas_glue.get(key)
            for imp in a:
                if imp in final_table:
                    pass
                else:
                    final_table[imp]=[]
        # в словарь добавляем первоначальные импликанты
        for i in range(len(mas_zero)):
            for key in final_table:
                kol=key.count('X')
                for j in range(len(mas_zero[i])):
                    if str(mas_zero[i][j])==key[j]:
                        kol+=1
                if kol==len(mas_zero[i]):
                    final_table[key].append(mas_zero[i])
        # составляем МКНФ
        mknf=[]
        for key in final_table.keys():
            a=final_table.get(key)
            count_X=key.count('X')
            if count_X==len(key):
                return 0
            if len(a)!=0:
                term=[]
                for j in range(len(key)):
                    if key[j]!='X':
                        if key[j]=='0':
                            term.append(var_names[j])
                        else:
                            term.append('!' + var_names[j])
                mknf.append('(' + '+'.join(term) + ')')
            for key1 in final_table.keys():
                if key1!=key:
                    b=final_table.get(key1)
                    for i in a:
                        for j in b:
                            if i==j:
                                final_table[key1].remove(j)
        return LogicFunction('*'.join(mknf))


def generate_function_from_table(table: list, method=0) -> LogicFunction:
    """Генерирует и возвращает объект LogicFunction по таблице истинности формата:
    list: [((tuple: input_values), result)]
    Используемые названия переменных: a, b, c, d...
    Args:
        table: list: [((tuple: input_values), result)]
        method: 0 - СДНФ, 1 - СКНФ

    Returns: объект LogicFunction с совершенной формой

    """
    snf = []  # список с логическими выражениями
    for line in table:
        term = []  # список одного логического выражения
        if line[1]==method:
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




tf = LogicFunction("А ИЛИ Б ИЛИ Б")
print(tf.get_current_expression())
print(tf.generate_boolean_table())
print(tf.simplify_sdnf().get_current_expression())