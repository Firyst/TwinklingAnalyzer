import pytest
from LogicFunction import *


def test_init_1():
    with pytest.raises(InputException):
        LogicFunction('')


def test_init_2():
    with pytest.raises(InputException):
        LogicFunction('a')


def test_init_3():
    with pytest.raises(InputException):
        LogicFunction('(+-!@#$%^&*=:;)')


def test_init_4():
    with pytest.raises(InputException):
        LogicFunction('fkjjsdflnsafb')


def test_init_5():
    with pytest.raises(InputException):
        LogicFunction('1234567890')


def test_init_6():
    with pytest.raises(InputException):
        LogicFunction('())))')


def test_init_7():
    f = LogicFunction("A      +     B")
    assert f.exp == 'A or B'


def test_init_8():
    f = LogicFunction("A*B+B")
    assert f.exp == 'A and B or B'


def test_init_9():
    f = LogicFunction("!AB+B^C")
    assert f.exp == ' not AB or B^C'


def test_init_10():
    f = LogicFunction("A+B^C*D")
    assert f.exp == 'A or B^C and D'


def test_init_11():
    with pytest.raises(InputException):
        LogicFunction('LONG_NAME and B')


def test_get_variables_1():
    f = LogicFunction("A+B^C*D")
    assert f.get_variables() == ['A', 'B', 'C', 'D']


def test_get_variables_2():
    f = LogicFunction("A^B*C*A+C")
    assert f.get_variables() == ['A', 'B', 'C']


def test_get_result_1():
    f = LogicFunction("A+B+C")
    assert f.get_result((0, 0, 0)) == 0


def test_get_result_2():
    f = LogicFunction("A+B")
    with pytest.raises(IndexError):
        f.get_result((0,))


def test_get_result_3():
    f = LogicFunction("A+B*C")
    assert f.get_result((0, 1, 1)) == 1


def test_generate_boolean_table_1():
    f = LogicFunction('A^B')
    assert f.generate_boolean_table() == [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]


def test_generate_boolean_table_2():
    f = LogicFunction('A+B*С')
    assert f.generate_boolean_table() == [((0, 0, 0), 0), ((0, 0, 1), 0), ((0, 1, 0), 0), ((0, 1, 1), 1),
                                          ((1, 0, 0), 1), ((1, 0, 1), 1), ((1, 1, 0), 1), ((1, 1, 1), 1)]


def test_simplyfy_sdnf_1():
    f = LogicFunction('A*B*C')
    assert f.generate_boolean_table() == f.simplify_sdnf().generate_boolean_table()


def test_simplyfy_sdnf_2():
    f = LogicFunction('!A*A*!B*B')
    with pytest.raises(InputException):
        f.simplify_sdnf()


def test_simplyfy_sdnf_3():
    f = LogicFunction('!A^B+!C^D*F')
    assert f.generate_boolean_table() == f.simplify_sdnf().generate_boolean_table()


def test_simplyfy_sknf_1():
    f = LogicFunction('A+B+C')
    assert f.generate_boolean_table() == f.simplify_sknf().generate_boolean_table()


def test_simplyfy_sknf_2():
    f = LogicFunction('!A+A+!B+B')
    with pytest.raises(InputException):
        f.simplify_sknf()


def test_simplyfy_sknf_3():
    f = LogicFunction('!A^B+!C^D*F')
    assert f.generate_boolean_table() == f.simplify_sknf().generate_boolean_table()
