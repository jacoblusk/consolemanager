import sys
import unittest
import logging
import types
import inspect
import consolemanager
from typing import *

class TestConsoleManager(unittest.TestCase):
    def run(self, result=None):
        with consolemanager.ConsoleManager(consolemanager.ConsoleStandardHandle.STD_OUTPUT_HANDLE) as console:
            self.console = console
            super(TestConsoleManager, self).run(result)

    def test_set_cursor_pos(self):
        csi = self.console.get_console_info()

        t_x = lambda x: x + 1
        t_y = lambda y: y - 1
        self.console.set_cursor_pos(t_x(csi.cursor_position.x), t_y(csi.cursor_position.y))
        csi_new = self.console.get_console_info()

        self.assertEqual(csi_new.cursor_position.x, t_x(csi.cursor_position.x))
        self.assertEqual(csi_new.cursor_position.y, t_y(csi.cursor_position.y))

    def test_read_console(self):
        #TODO This is wrong
        csi = self.console.get_console_info()

        output = self.console.read_console()
        assert(len(output), csi.size.y)

    def test_read_console_line(self):
        csi = self.console.get_console_info()

        old_sys_out = sys.stdout
        sys.stdout = sys.__stdout__

        self.console.set_cursor_pos(0, csi.window_rectangle.bottom)
        test_string = "1" * csi.window_rectangle.right
        print(test_string, end='', flush=True)
        result = self.console.read_console_line(csi.window_rectangle.bottom).strip()
        sys.stdout = old_sys_out

        self.assertEqual(test_string, result)

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    unittest.main()