import time


class Util:

    @classmethod
    def current_date(cls):
        """Fetch the current date for logging."""
        return time.strftime("%c")

    @classmethod
    def log(cls, msg, level="DEBUG", ):
        """Logging wrapper."""
        print "[%s] %s %s" % (Util.current_date(), level.upper(), msg)

    @classmethod
    def has_valid_config(cls, settings):
        """Very basic sanity checks for the configuration options."""
        if int(settings["quadrant_capture_count"]) == 3 or \
                int(settings["quadrant_capture_count"]) > 4:
            return "Invalid quadrant_capture_count value, must be 1, 2, or 4."
        if int(settings["quadrant_capture_count"]) == 2 and \
                not 1 <= int(settings["quadrant_number"]) <= 2:
            return "Invalid quadrant_number value, must be 1 or 2."

        return None

    @classmethod
    def resize_capture_area(cls, window_size, settings):
        """Adjust the capture area based on the quadrants specified in the config."""
        quadrant_capture_count = int(settings["quadrant_capture_count"])
        quadrant_number = int(settings["quadrant_number"])

        # Find a more elegant way to do this
        if quadrant_capture_count == 1:
            # User wants to capture 1 of the 4 quadrants
            return {
                # top left
                1: (window_size[0], window_size[1], window_size[2] / 2, window_size[3] / 2),
                # top right
                2: (window_size[3] / 2, window_size[1], window_size[2], window_size[3] / 2),
                # bottom left
                # tighter region for hots health bar (0, y * .8, x * .25, y)
                # 3: (window_size[0], window_size[3] * 0.8, window_size[2] *
                # 0.25, window_size[3]),
                3: (window_size[0], window_size[3] / 2, window_size[2] / 2, window_size[3]),
                #  3: (window_size[0] / 7, window_size[3] - (window_size[3] / 6), window_size[2] / 4, window_size[3]),
                # bottom right
                4: (window_size[2] / 2, window_size[3] / 2, window_size[2], window_size[3]),
            }.get(quadrant_number, window_size)

        if quadrant_capture_count == 2:
            return {
                # top
                # left top right bottom
                1: (window_size[0], window_size[1], window_size[2], window_size[3] / 2),
                # bottom
                2: (window_size[0], window_size[3] / 2, window_size[2], window_size[3]),
                # bottom left
                3: (window_size[0], window_size[3] / 2, window_size[2] / 2, window_size[3]),
                # bottom right
                4: (window_size[2] / 2, window_size[3] / 2, window_size[2], window_size[3]),
            }.get(quadrant_number, window_size)

        return window_size

    @classmethod
    def find_window_by_title(cls, title):
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

        Util.log("Found window with title %s" % title, "INFO")

        return window_size

    @classmethod
    def screenshot(cls, window):
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

    @classmethod
    def send_osc(cls, client, msg):
        """Sends an OSC message."""
        client.send(msg)
