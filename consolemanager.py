import ctypes
import enum

class _COORD(ctypes.Structure):
    _fields_ = [('X', ctypes.c_ushort),
                ('Y', ctypes.c_ushort)]

    def __repr__(self):
        return f"win32<{self.X}, {self.Y}>"


class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __to_win32_COORD(self):
        return _COORD(self.x, self.y)

    def __repr__(self):
        return f"<{self.x}, {self.y}>"

    @staticmethod
    def __from_win32_COORD(coord):
        return Vector2D(coord.X, coord.Y)


class _SMALL_RECT(ctypes.Structure):
    _fields_ = [('Left', ctypes.c_ushort),
                ('Top', ctypes.c_ushort),
                ('Right', ctypes.c_ushort),
                ('Bottom', ctypes.c_ushort)]


class Rectangle:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def __to_win32_SMALL_RECT(self):
        return _SMALL_RECT(self.left, self.top, self.right, self.bottom)

    def __repr__(self):
        return f"Rectangle<left:{self.left}, top:{self.top}, right:{self.right}, bottom:{self.bottom}>"

    @staticmethod
    def __from_win32_SMALL_RECT(small_rect):
        return Rectangle(small_rect.Left, small_rect.Top, small_rect.Right, small_rect.Bottom)


class _CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [('dwSize', _COORD),
                ('dwCursorPosition', _COORD),
                ('wAttributes', ctypes.c_ushort),
                ('srWindow', _SMALL_RECT),
                ('dwMaximumWindowSize', _COORD)]

    def __repr__(self):
        return f"dwCursorPosition: {self.dwCursorPosition}"
        

class ConsoleScreenInformation:
    def __init__(self, size: Vector2D, cursor_position: Vector2D, window_rectangle: Rectangle, maximum_window_size: Vector2D):
        self.size = size
        self.cursor_position = cursor_position
        self.window_rectangle = window_rectangle
        self.maximum_window_size = maximum_window_size

    def __to_win32_CONSOLE_SCREEN_BUFFER_INFO(self, attributes):
        return _CONSOLE_SCREEN_BUFFER_INFO(self.size, self.cursor_position, attributes, self.window_rectangle, self.maximum_window_size)

    def __repr__(self):
        return f"ConsoleScreenInformation<size:{self.size}, cursor_position:{self.cursor_position}, window_rectangle:{self.window_rectangle}, maximum_window_size:{self.maximum_window_size}>"

    @staticmethod
    def __from_win32_CONSOLE_SCREEN_BUFFER_INFO(info):
        return ConsoleScreenInformation(Vector2D._Vector2D__from_win32_COORD(info.dwSize),
                                        Vector2D._Vector2D__from_win32_COORD(info.dwCursorPosition),
                                        Rectangle._Rectangle__from_win32_SMALL_RECT(info.srWindow),
                                        Vector2D._Vector2D__from_win32_COORD(info.dwMaximumWindowSize))


class _CONSOLE_CURSOR_INFO(ctypes.Structure):
    _fields_ = [('dwSize', ctypes.c_ulong),
                ('bVisible', ctypes.c_int)]

    def __repr__(self):
        return f"win32<{self.dwSize}, {self.bVisible}>"


class CursorInformation:
    def __init__(self, size: int, visibility: bool):
        self.size = size
        self.visibility = visibility

    def __to_win32_CONSOLE_CURSOR_INFO(self):
        return _CONSOLE_SCREEN_BUFFER_INFO(self.size, 1 if self.visibility else 0)

    @staticmethod
    def __from_CONSOLE_CURSOR_INFO(info):
        return CursorInformation(info.dwSize, True if info.bVisible else False)

    def __repr__(self):
        return f"<{self.size}, {self.visibility}>"


STD_OUTPUT_HANDLE = -11
INVALID_HANDLE_VALUE = -1

class TextAttribute(enum.IntFlag):
    FOREGROUND_BLUE = 0x0001
    FOREGROUND_GREEN = 0x0002
    FOREGROUND_RED = 0x0004
    FOREGROUND_INTENSITY = 0x0008
    BACKGROUND_BLUE = 0x0010
    BACKGROUND_GREEN = 0x0020
    BACKGROUND_RED = 0x0040
    BACKGROUND_INTENSITY = 0x0080
    COMMON_LVB_LEADING_BYTE = 0x0100
    COMMON_LVB_TRAILING_BYTE = 0x0200
    COMMON_LVB_GRID_HORIZONTAL = 0x0400
    COMMON_LVB_GRID_LVERTICAL = 0x0800
    COMMON_LVB_GRID_RVERTICAL = 0x1000
    COMMON_LVB_REVERSE_VIDEO = 0x4000
    COMMON_LVB_UNDERSCORE = 0x8000

class ConsoleError(Exception):
    pass

def _general_windows_errcheck(result, func, args):
    if not result:
        raise ctypes.WinError(ctypes.get_last_error())

def _get_std_handle_errcheck(result, func, args):
    if result == ctypes.c_void_p(INVALID_HANDLE_VALUE):
        raise ctypes.WinError(ctypes.get_last_error())
    elif result is None:
        raise ConsoleError("The application does not have the associated standard handle provided.")
    return result
        
_GetStdHandle = ctypes.windll.kernel32.GetStdHandle
_GetStdHandle.argtypes = [ctypes.c_ulong]
_GetStdHandle.restype = ctypes.c_void_p
_GetStdHandle.errcheck = _get_std_handle_errcheck

_SetConsoleCursorPosition = ctypes.windll.kernel32.SetConsoleCursorPosition
_SetConsoleCursorPosition.argtypes = [ctypes.c_void_p, _COORD]
_SetConsoleCursorPosition.restype = ctypes.c_int
_SetConsoleCursorPosition.errcheck = _general_windows_errcheck

_GetConsoleScreenBufferInfo = ctypes.windll.kernel32.GetConsoleScreenBufferInfo
_GetConsoleScreenBufferInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(_CONSOLE_SCREEN_BUFFER_INFO)]
_GetConsoleScreenBufferInfo.restype = ctypes.c_int
_GetConsoleScreenBufferInfo.errcheck = _general_windows_errcheck

_FillConsoleOutputCharacterA = ctypes.windll.kernel32.FillConsoleOutputCharacterA
_FillConsoleOutputCharacterA.argtypes = [ctypes.c_void_p, ctypes.c_char, ctypes.c_ulong, _COORD, ctypes.POINTER(ctypes.c_ulong)]
_FillConsoleOutputCharacterA.restype = ctypes.c_int
_FillConsoleOutputCharacterA.errcheck = _general_windows_errcheck

_FillConsoleOutputAttribute = ctypes.windll.kernel32.FillConsoleOutputAttribute
_FillConsoleOutputAttribute.argtypes = [ctypes.c_void_p, ctypes.c_ushort, ctypes.c_ulong, _COORD, ctypes.POINTER(ctypes.c_ulong)]
_FillConsoleOutputAttribute.restype = ctypes.c_int
_FillConsoleOutputAttribute.errcheck = _general_windows_errcheck

_SetConsoleCursorInfo = ctypes.windll.kernel32.SetConsoleCursorInfo
_SetConsoleCursorInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(_CONSOLE_CURSOR_INFO)]
_SetConsoleCursorInfo.restype = ctypes.c_int
_SetConsoleCursorInfo.errcheck = _general_windows_errcheck

_GetConsoleCursorInfo = ctypes.windll.kernel32.GetConsoleCursorInfo
_GetConsoleCursorInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(_CONSOLE_CURSOR_INFO)]
_GetConsoleCursorInfo.restype = ctypes.c_int
_GetConsoleCursorInfo.errcheck = _general_windows_errcheck

_SetConsoleTextAttribute = ctypes.windll.kernel32.SetConsoleTextAttribute
_SetConsoleTextAttribute.argtypes = [ctypes.c_void_p, ctypes.c_ushort]
_SetConsoleTextAttribute.restype = ctypes.c_int
_SetConsoleTextAttribute.errcheck = _general_windows_errcheck

_SetConsoleTitleW = ctypes.windll.kernel32.SetConsoleTitleW
_SetConsoleTitleW.argtypes = [ctypes.c_wchar_p]
_SetConsoleTitleW.restype = ctypes.c_int
_SetConsoleTitleW.errcheck = _general_windows_errcheck


class ConsoleStandardHandle(enum.IntEnum):
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12

class Console:
    CONSOLE_COLOR_ATTRIBUTE_MAP = {
        'black': 0x0,
        'blue': 0x1,
        'green': 0x2,
        'aqua': 0x3,
        'red': 0x4,
        'purple': 0x5,
        'yellow': 0x6,
        'white': 0x7,
        'gray': 0x8,
        'light blue': 0x9,
        'light green': 0xA,
        'light aqua': 0xB,
        'light red': 0xC,
        'light purple': 0xD,
        'light yellow': 0xE,
        'bright white': 0xF
    }
    
    def __init__(self, std_handle=ConsoleStandardHandle.STD_INPUT_HANDLE):
        self.handle = _GetStdHandle(std_handle)
        self.__default_cursor_info = self.__get_win32_cursor_info()
        self.__default_console_info = self.__get_win32_console_screen_buffer_info()

        
    def clear_screen(self, char=' '):
        coord_screen = _COORD(0, 0)
        chars_written = ctypes.c_ulong(0)
        csbi = _CONSOLE_SCREEN_BUFFER_INFO()
        console_size = ctypes.c_ulong(0)

        _GetConsoleScreenBufferInfo(self.handle, ctypes.byref(csbi))
        console_size = csbi.dwSize.X * csbi.dwSize.Y
        
        _FillConsoleOutputCharacterA(self.handle, ctypes.c_char(ord(char)), console_size, coord_screen, ctypes.byref(chars_written))
        _GetConsoleScreenBufferInfo(self.handle, ctypes.byref(csbi))
        _FillConsoleOutputAttribute(self.handle, csbi.wAttributes, console_size, coord_screen, ctypes.byref(chars_written))
        _SetConsoleCursorPosition(self.handle, coord_screen)

    def set_title(self, title):
        unicode_buffer = ctypes.create_unicode_buffer(title)
        _SetConsoleTitleW(unicode_buffer)

    def set_default_cursor_info(self):
        _SetConsoleCursorInfo(self.handle, ctypes.byref(self.__default_cursor_info))

    def set_default_text_color(self):
        self.__set_text_attribute(self.__default_console_info.wAttributes)
    
    def get_cursor_info(self):
        cci = self.__get_win32_cursor_info()
        return CursorInformation._CursorInformation__from_CONSOLE_CURSOR_INFO(cci)

    def __get_win32_cursor_info(self):
        cci_out = _CONSOLE_CURSOR_INFO()
        _GetConsoleCursorInfo(self.handle, ctypes.byref(cci_out))
        return cci_out

    def get_console_info(self):
        csbi = self.__get_win32_console_screen_buffer_info()
        return ConsoleScreenInformation._ConsoleScreenInformation__from_win32_CONSOLE_SCREEN_BUFFER_INFO(csbi)

    def __get_win32_console_screen_buffer_info(self):
        csbi = _CONSOLE_SCREEN_BUFFER_INFO()
        _GetConsoleScreenBufferInfo(self.handle, ctypes.byref(csbi))
        return csbi
    
    def set_cursor_info(self, size: int, visibility: bool):
        if size < 1 or size > 100:
            raise ConsoleError("Size must be between 1 and 100")

        cci = _CONSOLE_CURSOR_INFO(size, 1 if visibility else 0)
        _SetConsoleCursorInfo(self.handle, ctypes.byref(cci))

    def __set_text_attribute(self, attributes: TextAttribute):
        _SetConsoleTextAttribute(self.handle, attributes)

    def set_cursor_pos(self, x, y):
        coord_screen = _COORD(x, y)
        _SetConsoleCursorPosition(self.handle, coord_screen)

    def set_text_color(self, foreground: str, background: str):
        if foreground not in Console.CONSOLE_COLOR_ATTRIBUTE_MAP:
            raise ConsoleError("Unable to find foreground color.")
        
        if background not in Console.CONSOLE_COLOR_ATTRIBUTE_MAP:
            raise ConsoleError("Unable to find background color.")
        _SetConsoleTextAttribute(self.handle, Console.CONSOLE_COLOR_ATTRIBUTE_MAP[background.lower()] << 4 | \
                                              Console.CONSOLE_COLOR_ATTRIBUTE_MAP[foreground.lower()])
    
    def clear_line(self, y):
        coord_screen = _COORD(0, y)
        chars_written = ctypes.c_ulong(0)

        console_info = self.__get_win32_console_screen_buffer_info()
        _FillConsoleOutputCharacterA(self.handle, ctypes.c_char(ord(' ')),
                                     console_info.srWindow.Right, coord_screen,
                                     ctypes.byref(chars_written))


class ConsoleManager:
    def __init__(self, std_handle=ConsoleStandardHandle.STD_INPUT_HANDLE):
        self.console = Console(std_handle)

    def __enter__(self):
        return self.console

    def __exit__(self, type_, value, traceback):
        self.console.set_default_cursor_info()
        self.console.set_default_text_color()
            

