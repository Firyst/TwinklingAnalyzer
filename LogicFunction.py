from itertools import product
from string import punctuation


# словарь замен для представления функции в стандартном python виде
REPLACES = {' and ': ['&&', '*', ' и ', ' AND ', ' И ', '&'],
            ' or ': ['||', '+', ' или ', ' OR ', ' ИЛИ ', '|'],
            ' not ': ['!', ' NOT ', ' не ', ' НЕ '],
            ' ^ ': [' xor ', ' XOR ', '==']}


class LogicFunction:
    def __init__(self, expression: str):
        self.exp = expression
        for repl_symbol in REPLACES:
            for possible_entry in REPLACES[repl_symbol]:
                self.exp = self.exp.replace(possible_entry, repl_symbol)

    def get_current_expression(self) -> str:
        """
        Получить текущую запись логической функции.
        Returns: строка, отображающая логическую функцию с python-совместимыми операторами

        """
        return self.exp

    def get_variables(self):
        """
        Получить названия всех переменных в функции
        Returns: отсортированный list названий переменных

        """
        variables_left = self.exp
        for replacing_symbol in punctuation:
            # замена скобок
            variables_left = variables_left.replace(replacing_symbol, ' ')

        for operand in REPLACES.keys():
            # операнды - это не переменные, их заменяем
            variables_left = variables_left.replace(operand, ' ')

        return sorted(list(set(variables_left.split())))

    def get_function_result(self, values) -> int:
        """
        Выполнить функцию с определенными значениями переменных.
        Args:
            values: Итерируемый объект из 1 и 0. Переменные подаются в таком же порядке,
            в котором они возвращаются функцией get_variables()

        Returns: result of running function with set values
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
        """
        Генерирует таблицу истинности для логической функции
        Returns: list of tuples ((tuple: input_values), result)
        """
        func_vars = self.get_variables()  # get all variables
        result = []
        for func_case in product((0, 1), repeat=len(func_vars)):
            case_result = self.get_function_result(func_case)
            result.append((func_case, case_result))
        return result

    def beautiful_boolean_table(self):
        """
        Генерирует визуализацию таблицы истинности для print.
        Returns: отформатированная строка

        """
        table = self.generate_boolean_table()
        result = '\t'.join(self.get_variables() + ['func'])
        for case in table:
            result += '\n' + '\t'.join(map(str, case[0])) + f"\t{str(case[1])}"
        return result

    def generate_pdnfs(self):
        """
        PDNF (perfect disjunctive normal form), или СДНФ.
        Returns: объект LogicFunction в СДНФ

        """
        pass

    def generate_pcnfs(self):
        """
        PCNF (perfect conjunctive normal form), или СКНФ.
        Returns: объект LogicFunction в СКНФ

        """
        pass

    def simplify(self, method=0):
        """
        Упрощение методом Квайна
        Args:
            method: 0 - упрощение к МДНФ; 1 - урощение к МКНФ

        Returns: объект LogicFunction с упрощенной функцией

        """
        pass
