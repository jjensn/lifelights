import time


class Util:

    @classmethod
    def current_date(self):
        """Fetch the current date for logging."""
        return time.strftime("%c")

    @classmethod
    def log(self, msg, level="DEBUG"):
        """Logging wrapper."""
        print "[%s] %s %s" % (Util.current_date(), level.upper(), msg)

    @classmethod
    def find_window_by_title(self, title):
        """Find a Win32 window by title."""
        import win32gui
        import ctypes
        from ctypes.wintypes import DWORD, HWND

        hwnd = win32gui.FindWindow(None, title)
        if hwnd is None or hwnd is 0:
            return None

        # Windows 7 and higher uses invisible borders and GetWindowRect returns
        # the 'wrong' values
        try:
            window = ctypes.windll.dwmapi.DwmGetWindowAttribute
        except WindowsError:
            window = None

        if window:
            rect = ctypes.wintypes.RECT()
            DWMWA_EXTENDED_FRAME_BOUNDS = 9
            window(
                ctypes.wintypes.HWND(hwnd),
                ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
                ctypes.byref(rect), ctypes.sizeof(rect))
            # window_size = (rect.left, rect.bottom / 2, rect.right / 2,
            #               rect.bottom)
            window_size = (rect.left, rect.top, rect.right, rect.bottom)
        else:
            window_size = win32gui.GetWindowRect(hwnd)

        Util.log("Found a %s window with dimensions %s" % (title, window_size))

        return window_size

    @classmethod
    def screenshot(self, window):
        """Take a screenshot of a particular portion of the screen."""
        import numpy as np
        import cv2
        from PIL import ImageGrab

        try:
            screen = ImageGrab.grab(window)
            bgr_screen = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
            return bgr_screen
        except Exception:
            return np.array([])
