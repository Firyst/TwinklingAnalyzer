from itertools import product
from string import punctuation, ascii_letters, digits


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
        print(eval_string)
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

    def simplify(self, method=0):
        """Упрощение методом Квайна
        Args:
            method: 0 - упрощение к МДНФ; 1 - урощение к МКНФ

        Returns: объект LogicFunction с упрощенной функцией

        """
        pass


def generate_function_from_table(table: list, method=0) -> LogicFunction:
    """Генерирует и возвращает объект LogicFunction по таблице истинности формата:
    list: [((tuple: input_values), result)]
    Используемые названия переменных: a, b, c, d...
    Args:
        table: list: [((tuple: input_values), result)]
        method: 0 - СДНФ, 1 - СКНФ

    Returns: объект LogicFunction с совершенной формой

    """

'''
tf = LogicFunction("А ИЛИ Б И НЕ В")
print(tf.get_current_expression())
print(tf.generate_boolean_table())'''