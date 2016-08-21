import unittest
import time

from backend.components.dependancy import Condition
from backend.components.dependancy import Effect
from backend.components.dependancy import Dependancy
from backend.components.dependancy import DependancyConfigError

from backend.components.element import Element, OutputElement
from backend.components.clock import Clock


class TestCondition(unittest.TestCase):

    def setUp(self):
        id, op, self.comp_val = 1, "=", 20
        self.condition = Condition(id, op, comp_val=self.comp_val)

    def test_notify(self):
        # when
        self.condition.notify(5)

        # then
        self.assertEqual(self.condition.val, 5)

    def test_evaluate_false(self):
        # given
        notify_val = 5

        # when
        self.condition.notify(notify_val)
        result = self.condition.evaluate()

        # then
        self.assertFalse(eval(result))

    def test_evaluate_true(self):
        # when
        self.condition.notify(self.comp_val)
        result = self.condition.evaluate()

        # then
        self.assertTrue(eval(result))


class TestEffect(unittest.TestCase):

    def setUp(self):
        self.clock = Clock()

        el_id, _type, name, mod_id, reg_id = 0, 1, '', 0, 0
        self.output_element = OutputElement(el_id, _type, name, mod_id, reg_id)

        ef_id, value, _time = 0, 1, 1
        self.effect = Effect(ef_id, self.output_element, value, _time)

    def test_start(self):
        # when cause time is 1000ms
        self.effect.start(1000)

        # then effects cause time should be set to 1000ms and out_el value should be saved
        self.assertEqual(self.effect.cause_time, 1000)
        self.assertEqual(self.effect.prev_value, self.output_element.value)

    def test_run_cause_is_before_effect_time(self):
        # given effect time 1ms after cause
        self.effect.time = 1

        # when
        self.effect.start(self.clock.get_millis())
        time.sleep(0.001)

        # then
        self.assertTrue(self.effect.run())  # effect should happen
        self.assertEqual(self.output_element.desired_value, self.effect.value)

    def test_run_more_times(self):
        # given
        self.effect.time = 0
        # when
        self.effect.start(self.clock.get_millis())
        time.sleep(0.001)

        # then Effect should happen only once
        self.assertTrue(self.effect.run())  # effect should happen
        self.assertFalse(self.effect.run())  # effect should not happen
        self.assertFalse(self.effect.run())  # effect should not happen

    def test_revert_set(self):

        # when normal effect flow
        self.effect.start(self.clock.get_millis())
        time.sleep(0.001)
        self.effect.run()
        self.effect.revert()

        # then output_element desired value should be reverted
        self.assertEqual(self.output_element.desired_value, self.effect.prev_value)


class TestDependancy(unittest.TestCase):

    def setUp(self):
        self.clock = Clock()
        dep_id, name = 0, ''
        dep_str = '[e1=2] and [e2=3] and [d=mon] and [t=5:30] then e3=20{0}; e3=0{200}; e4=1{0}'

        self.dep = Dependancy(dep_id, name, dep_str)

    def test_find_condition(self):

        find_condition = self.dep._find_condition()
        self.assertEqual('e1=2', next(find_condition))
        self.assertEqual('e2=3', next(find_condition))
        self.assertEqual('d=mon', next(find_condition))
        self.assertEqual('t=5:30', next(find_condition))

        self.assertEqual(self.dep.cause_template, '! and ! and ! and !')

    def test_parse_condition(self):
        # given
        condition_str_day = 'd=mon,tue,wed,thu,fri'

        # when
        element, op, comp_value = self.dep._parse_condition(condition_str_day)

        # then
        self.assertEqual((element, op, comp_value), ('d', '=', 'mon,tue,wed,thu,fri'))

    def test_parse_cause(self):
        # given
        element_dict = {1: Element(1, 1, '', 1, 1), 2: Element(2, 1, '', 1, 1)}

        # when
        self.dep._parse_cause(all_elements=element_dict)

        # then found all conditions
        self.assertEqual(self.dep.num_of_conds, 4)

        # then all conditions are subscribed to elemenets
        self.assertIn(self.dep.conditions[0], element_dict[1].objects_to_notify)
        self.assertIn(self.dep.conditions[1], element_dict[2].objects_to_notify)
        self.assertIn(self.dep.conditions[2], self.clock.objects_to_notify_weekday)
        self.assertIn(self.dep.conditions[3], self.clock.objects_to_notify_time)

    def test_parse_effect_good_data(self):
        self.assertEqual(self.dep._parse_effect('e3=20{0}'), (3, 20, 0))

    def test_parse_effect_wrong_element_marker(self):
        with self.assertRaises(DependancyConfigError):
            self.dep._parse_effect('3=20{0}')

    def test_parse_effect_negative_element_time(self):
        with self.assertRaises(DependancyConfigError):
            self.dep._parse_effect('e3=20{-5}')

    def test_parse_effect_negative_value(self):
        with self.assertRaises(DependancyConfigError):
            self.dep._parse_effect('e3=-20{0}')

    def test_parse_effect_no_element_id(self):
        with self.assertRaises(DependancyConfigError):
            self.dep._parse_effect('e=20{0}')

    def test_parse_effect_value_is_char(self):
        with self.assertRaises(DependancyConfigError):
            self.dep._parse_effect('e=s{0}')

    def test_parse_effect_empty_effect_string(self):
        with self.assertRaises(DependancyConfigError):
            self.dep._parse_effect('')

    def test_parse_effects_all_efects_found(self):
        # given
        element_dict = {3: Element(3, 1, '', 1, 1), 4: Element(4, 1, '', 1, 1)}

        # when
        self.dep._parse_effects(output_elements=element_dict)

        # then
        self.assertEqual(self.dep.num_of_effect, 3)
