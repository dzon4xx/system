import unittest

from backend.components.element import Element, OutputElement, Blind
from backend.components.tests.helper_classes import Notifiable


class TestElement(unittest.TestCase):

    def setUp(self):
        id, type, name, module_id, reg_id = 0, 1, '', 0, 0
        self.element = Element(id, type, name, module_id, reg_id)
        self.notifiable = Notifiable()

    def test_subscribe(self):

        self.element.subscribe(self.notifiable)

        self.assertIn(self.notifiable, self.element.objects_to_notify)

    def test_notify_objects(self):

        self.element.subscribe(self.notifiable)
        self.element.value = 10
        self.element.notify_objects()
        self.assertEqual(self.element.value, self.notifiable.val)


class TestOutputElement(unittest.TestCase):

    def test_set_desired_value(self):
        id, type, name, module_id, reg_id = 0, 1, '', 0, 0
        value = 10

        output_element = OutputElement(id, type, name, module_id, reg_id)
        priority = output_element.setter_priority - 5  # lower priority should set
        set_flag = True
        self.assertEqual(output_element.set_desired_value(value, priority, set_flag=set_flag), True)
        self.assertEqual(output_element.desired_value, value)
        self.assertEqual(output_element.setter_priority, priority)

        output_element = OutputElement(id, type, name, module_id, reg_id)
        priority = output_element.setter_priority + 5  # higher priority shouldn't set
        set_flag = True
        self.assertEqual(output_element.set_desired_value(value, priority, set_flag=set_flag), False)
        self.assertEqual(output_element.desired_value, 0)
        self.assertEqual(output_element.setter_priority, output_element.defualt_priority)

        output_element = OutputElement(id, type, name, module_id, reg_id)
        priority = output_element.setter_priority - 5  # lower priority should set
        set_flag = False  # priority should be restored to default value
        self.assertEqual(output_element.set_desired_value(value, priority, set_flag=set_flag), True)
        self.assertEqual(output_element.desired_value, value)
        self.assertEqual(output_element.setter_priority, output_element.defualt_priority)

    def test_blind_set_value(self):
        id, type, name, module_id, reg_id, = 0, 1, '', 0, 0

        blind_up = Blind(0, type, name, module_id, reg_id, 'up', None)
        blind_down = Blind(1, type, name, module_id, reg_id, 'down', blind_up)
        blind_up.other_blind = blind_down
        blind_up.desired_value = 100
        blind_down.desired_value = 100

        value = 1
        priority = OutputElement.defualt_priority - 5  # lower priority should set
        set_flag = True

        blind_up.set_desired_value(value, priority, set_flag)
        self.assertEqual(blind_up.desired_value, value)
        self.assertEqual(blind_up.other_blind.desired_value, 0)