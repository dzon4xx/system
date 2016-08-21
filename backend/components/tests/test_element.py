import unittest

from backend.components.element import Element, OutputElement, Blind
from backend.components.tests.helper_classes import Notifiable


class TestElement(unittest.TestCase):

    def setUp(self):
        id, type, name, module_id, reg_id = 0, 1, '', 0, 0
        self.element = Element(id, type, name, module_id, reg_id)
        self.notifiable = Notifiable()

    def test_subscribe_notifiable(self):
        # when
        self.element.subscribe(self.notifiable)

        # then
        self.assertIn(self.notifiable, self.element.objects_to_notify)

    def test_notify_objects(self):
        # given
        self.element.value = 10

        # when
        self.element.subscribe(self.notifiable)
        self.element.notify_objects()

        # then
        self.assertEqual(self.element.value, self.notifiable.val)


class TestOutputElement(unittest.TestCase):

    def setUp(self):
        self.output_element = OutputElement(0, 1, '', 0, 0)
        self.value, self.priority, self.set_flag = 10, 5, True

    def test_set_desired_value_when_priority_is_lower_than_default(self):
        # when
        self.output_element.set_desired_value(self.value, self.priority, self.set_flag)

        # then
        self.assertEqual(self.output_element.desired_value, self.value)

    def test_not_set_desired_value_when_priority_is_higher_than_default(self):
        # given
        self.priority = 20

        # when
        self.output_element.set_desired_value(self.value, self.priority, self.set_flag)

        # then
        self.assertEqual(self.output_element.desired_value, 0)

    def test_set_priority_when_set_flag_true(self):
        # when
        self.output_element.set_desired_value(self.value, self.priority, self.set_flag)

        # then
        self.assertEqual(self.output_element.setter_priority, self.priority)

    def test_reset_setter_priority_when_set_flag_false(self):
        #given
        self.set_flag = False

        # when
        self.output_element.set_desired_value(self.value, self.priority, self.set_flag)

        # then
        self.assertEqual(self.output_element.setter_priority, self.output_element.defualt_priority)

    def test_set_other_blind_desired_value_to_0(self):

        # given
        id, type, name, module_id, reg_id, = 0, 1, '', 0, 0
        blind_up = Blind(0, type, name, module_id, reg_id, 'up', None)
        blind_down = Blind(1, type, name, module_id, reg_id, 'down', blind_up)
        blind_up.other_blind = blind_down
        blind_up.desired_value = 100
        blind_down.desired_value = 100

        # when
        blind_up.set_desired_value(self.value, self.priority, self.set_flag)

        # then
        self.assertEqual(blind_up.desired_value, self.value)
        self.assertEqual(blind_up.other_blind.desired_value, 0)