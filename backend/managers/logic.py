import logging
import queue
import threading
import time

from backend.components.clock import Clock
from backend.misc.sys_types import Et


class LogicManager(threading.Thread):

    clock = Clock()

    def __init__(self, args=(),):
        threading.Thread.__init__(self, group=None, target=None, name='LOGIC')
        self._comunication_out_buffer = args[0]
        self._comunication_in_buffer = args[1]
        system = args[2]
        self.elements = system.elements.all
        self.output_elements = system.elements.output
        self.output_modules = system.modules.output
        self.regulations = system.regulations
        self.dependancies = system.dependancies

        self._client_priority = 5
        self.logger = logging.getLogger('LOGIC')
        self.tasks = queue.Queue()

    def set_desired_value(self, _type, _id, value, _msg):
        """Sets elements desired values"""
        if _type == 'e':
            set_flag = False
            if value > 0:
                set_flag = True
            self.output_elements[_id].set_desired_value(value, self._client_priority,
                                                        set_flag)  # Client has low priority.
            self.logger.debug('Set desired value el: %s val: %s', _id, value)
        elif _type == 'r':
            self.regulations[_id].set_point = value
            self._comunication_in_buffer.put(_msg)  # Ack that regulation was set
            # self.logger.debug(self.output_elements.str())

    def process_input_communication(self, ):
        """Checks if there are any commands from client. """

        def parse_msg(msg):
            try:
                msg = msg.split(',')
                _type = msg[0][0]
                _id = int(msg[0][1:])
                value = int(msg[1])
            except:
                return None
            return _type, _id, value

        while not self._comunication_out_buffer.empty():
            msg = self._comunication_out_buffer.get()
            self.logger.debug(msg)
            _type, _id, value = parse_msg(msg)
            if not msg:
                yield None
            yield _type, _id, value, msg

    def _check_elements_values_and_notify(self, ):
        """Check elements new value flags which are set by modbus.
        If there are new values notify interested components and put message to communication thread"""
        for element in self.elements.values():
            if element.new_val_flag:
                self.logger.debug(element)
                element.notify_objects()  # Notifies objects which are interested
                element.new_val_flag = False
                if element.type in (Et.pir, Et.rs, Et.switch, Et.heater, Et.blind):
                    msg = 'e' + str(element.id) + ',' + str(element.value) + ',' + 's'
                else:
                    msg = 'e' + str(element.id) + ',' + str(element.value)                   
                yield msg

    def _run_relations(self, ):
        """Runs dependancies and regulations"""

        for dep in self.dependancies.values():
            dep.run() 

        for reg in self.regulations.values():
            reg.run()

    def _generate_new_tasks(self,):
        """Generates queue with modules which have elements with changed value"""
        modules_to_notify = set()
        for out_element in self.output_elements.values():
            if out_element.value != out_element.desired_value:
                modules_to_notify.add(self.output_modules[out_element.module_id])

        while modules_to_notify:
            self.tasks.put(modules_to_notify.pop())

    def run(self, ):
        """Main logic loop"""
        self.logger.info('Thread {} start'. format(self.name))
        while True:            
            self.clock.evaluate_time()

            for msg in self.process_input_communication():
                self.set_desired_value(*msg)

            for ack_msg in self._check_elements_values_and_notify():
                self._comunication_in_buffer.put(ack_msg)

            self._run_relations()
            self._generate_new_tasks()
            time.sleep(0.1)

