import unittest
import logging
from collections import namedtuple

from backend.components.dependancy import Condition
from backend.components.dependancy import Effect
from backend.components.dependancy import Dependancy
from backend.components.dependancy import get_millis
from backend.components.dependancy import DependancyConfigError

from backend.components.element import Element, OutputElement
from backend.components.clock import Clock


class TestCondition(unittest.TestCase):

    def test_notify(self):
        condition = Condition(1, "=", 20)
        condition.notify(5)
        self.assertEqual(condition.val, 5)

    def test_evaluate(self):

        comp_val = 20
        notify_val = 5

        condition = Condition(1, "=", comp_val)

        condition.notify(notify_val)
        result = condition.evaluate()
        self.assertFalse(eval(result))

        condition.notify(comp_val)
        result = condition.evaluate()
        self.assertTrue(eval(result))


class TestEffect(unittest.TestCase):

    def test_parse_time(self):

        effect = Effect(0, 5, 5, '12')
        self.assertEqual(effect.time, 12000)

        effect = Effect(0, 5, 5, ' 12 ')
        self.assertEqual(effect.time, 12000)

        with self.assertRaises(DependancyConfigError):
            Effect(0, 5, 5, 'a')

        with self.assertRaises(DependancyConfigError):
            Effect(0, 5, 5, None)

        effect = Effect(0, 5, 5, 12)
        self.assertEqual(effect.time, 12000)

    def test_notify(self):

        output_el = namedtuple("Output_element", "value", "desired_value")
        output_el.value = 20

        effect = Effect(0, output_el, 5, '12')

        effect.notify(2500)

        self.assertEqual(effect.cause_time, 2500)
        self.assertEqual(effect.prev_value, output_el.value)

    def test_run(self):

        output_el = OutputElement(0, 1, '', 0, 0)

        value = 5
        effect_time = 0
        effect = Effect(0, output_el, value, effect_time)

        effect.notify(get_millis())

        self.assertTrue(effect.run())  # effect should happen
        self.assertEqual(output_el.desired_value, value)

        value = 5
        effect_time = 1
        effect = Effect(0, output_el, value, effect_time)

        effect.notify(get_millis())
        self.assertFalse(effect.run())  # effect shouldn't happen

    def test_revert_set(self):

        output_el = OutputElement(0, 1, '', 0, 0)
        output_el.value = 20

        value = 5
        effect_time = 0
        effect = Effect(0, output_el, value, effect_time)

        effect.notify(get_millis())
        effect.run()
        effect.revert()
        self.assertEqual(output_el.desired_value, (effect.prev_value, effect.priority, False))


class TestDependancy(unittest.TestCase):

    def setUp(self):
        dep_str = '[e1=2] and [e2=3] and [d=mon] and [t=5:30] then e3=20{0}; e3=0{200}; e4=1{0}'

        self.dep = Dependancy(1, '', dep_str)

    def test_find_condition(self):

        find_condition = self.dep._find_condition()
        self.assertEqual('e1=2', next(find_condition))
        self.assertEqual('e2=3', next(find_condition))
        self.assertEqual('d=mon', next(find_condition))
        self.assertEqual('t=5:30', next(find_condition))

        self.assertEqual(self.dep.cause_template, '! and ! and ! and !')

    def test_parse_condition(self):

        condition_str_day = 'd=mon,tue,wed,thu,fri'

        element, op, comp_value = self.dep._parse_condition(condition_str_day)
        self.assertEqual((element, op, comp_value), ('d', '=', 'mon,tue,wed,thu,fri'))

    def test_parse_cause(self):

        element_dict = {1: Element(1, 1, '', 1, 1), 2: Element(2, 1, '', 1, 1)}
        clock = Clock()

        self.dep._parse_cause(all_elements=element_dict, clock=clock)

        self.assertEqual(self.dep.num_of_conds, 4)

        self.assertIn(self.dep.conditions[0], element_dict[1].objects_to_notify)
        self.assertIn(self.dep.conditions[1], element_dict[2].objects_to_notify)
        self.assertIn(self.dep.conditions[2], clock.objects_to_notify_weekday)
        self.assertIn(self.dep.conditions[3], clock.objects_to_notify_time)

    def test_parse_effect(self):

        self.assertEqual(self.dep._parse_effect('e3=20{0}'), (3, 20, 0))

        with self.assertRaises(DependancyConfigError):
            self.dep._parse_effect('3=20{0}')

        with self.assertRaises(DependancyConfigError):
            self.dep._parse_effect('e3=20{-5}')
            print(DependancyConfigError.msg)

        with self.assertRaises(DependancyConfigError):
            self.dep._parse_effect('e3=-20{0}')
            print(DependancyConfigError.msg)

        with self.assertRaises(DependancyConfigError):
            self.dep._parse_effect('e=20{0}')

        with self.assertRaises(DependancyConfigError):
            self.dep._parse_effect('e=s{0}')

        with self.assertRaises(DependancyConfigError):
            self.dep._parse_effect('')

    def test_parse_effects(self):

        element_dict = {3: Element(3, 1, '', 1, 1), 4: Element(4, 1, '', 1, 1)}

        self.dep._parse_effects(output_elements=element_dict)

        self.assertEqual(self.dep.num_of_effect, 3)

        #effect_1, effect_2, effect_3 = self.dep.effects






