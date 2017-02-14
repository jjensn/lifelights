import requests as req
import json
import time
import OSC
import numpy as np
from util import Util
import cv2


class WidthWatcher:
    """Performs scanning and sizing of an image based on upper and lower bounds of colors."""

    def __init__(self, watcher_conf):
        self._settings = watcher_conf
        self._upper_bounds = (watcher_conf["color_upper_limit"]["blue"],
                              watcher_conf["color_upper_limit"]["green"],
                              watcher_conf["color_upper_limit"]["red"])

        self._lower_bounds = (watcher_conf["color_lower_limit"]["blue"],
                              watcher_conf["color_lower_limit"]["green"],
                              watcher_conf["color_lower_limit"]["red"])

        self._max_width = 1.0
        self._width = 0.0
        self._osc_client = None

        self._last_percentage = 0.0

        self._debug = "debug" in self._settings and self._settings["debug"]

        self._blur_amount = self._settings['blur_amount']

        if self._debug:
            cv2.namedWindow(self._settings["name"])
            cv2.createTrackbar('blur', self._settings[
                "name"], self._blur_amount, 50, self.onTrackbarChange)

    def onTrackbarChange(self, trackbarValue):
        """Empty function for debugging."""
        self._blur_amount = trackbarValue

    def scan(self, screen):
        """Scan an image and attempt to fit an invisible rectangle around a group of colors."""

        if self._debug:
            trackbar = cv2.getTrackbarPos('blur', self._settings["name"])

            if (trackbar % 2 == 0):
                self._blur_amount = trackbar + 1

        blur = cv2.medianBlur(screen, self._blur_amount)

        image_mask = cv2.inRange(blur, self._lower_bounds, self._upper_bounds)

        cnts = cv2.findContours(image_mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[-2]
        if len(cnts) > 0:
            max_cnt = max(cnts, key=cv2.contourArea)
            left, top, width, height = cv2.boundingRect(max_cnt)

            if self._max_width < width:
                self._max_width = float(width)
                if self._debug:
                    Util.log("Max %s updated %d" %
                             (self._settings["name"], width))

            self._width = float(width)

            if self._debug:
                cv2.rectangle(blur, (left, top),
                              (left + width, top + height), (0, 255, 0), 2)
        else:
            self._width = 0.0

        if self._debug:
            # cv2.drawContours(closing, cnts, -1, (0,255,0), 3)
            cv2.imshow(self._settings["name"], blur)
            cv2.waitKey(100)

    def process(self):
        """Execute RESTful API calls based on the results of an image scan."""
        import copy

        percent = round((self._width * 1.0) / (self._max_width * 1.0), 2)

        if self._last_percentage == percent:
            return

        if percent + (self._settings["change_threshold"] * 1.0 / 100) > 1.0:
            # snap to 100%
            percent = 1.0
        elif percent - (self._settings["change_threshold"] * 1.0 / 100) < 0.0:
            # snap to 0%
            percent = 0.0

        if abs(self._last_percentage - percent) < (self._settings["change_threshold"] * 1.0) / 100:
            return

        self._last_percentage = float(percent)

        if percent <= 0.0:
            Util.log("%s reached 0.0" %
                     self._settings["name"], "INFO")
        else:
            Util.log("%s updated to %.2f" %
                     (self._settings["name"], percent), "INFO")

        try:
            rgb = [
                int(255 * (100 - (percent * 100)) / 100),
                int(255 * (percent * 100) / 100), 0
            ]

            settings_copy = copy.deepcopy(self._settings)

            for index, request in enumerate(settings_copy["requests"]):
                for payload, value in request["payloads"].items():
                    if value == "LIFELIGHT_RGB":
                        settings_copy["requests"][index]["payloads"][
                            payload] = rgb
                    if value == "LIFELIGHT_RECT_WIDTH":
                        settings_copy["requests"][index]["payloads"][
                            payload] = int(self._width)
                    if value == "LIFELIGHT_PERCENT":
                        settings_copy["requests"][index]["payloads"][
                            payload] = int((percent * 100))
                    # if value == "LIFELIGHT_RECT":
                    #     settings_copy["requests"][index]["payloads"][
                    #         payload] = int((percent * 255))
                    if value == "LIFELIGHT_RAW_PERCENT":
                        settings_copy["requests"][index]["payloads"][
                            payload] = percent

                if "pre_api_delay" in request:
                    time.sleep(float(request["pre_api_delay"]))

                if self._debug:
                    Util.log("sending %s" % json.dumps(request["payloads"]))

                if request["method"].upper() == "POST":
                    api_call = req.post(
                        request["endpoint"],
                        data=json.dumps(request["payloads"]))
                if request["method"].upper() == "GET":
                    api_call = req.get(
                        request["endpoint"],
                        data=request["payloads"])
                if request["method"].upper() == "OSC":
                    # osc streaming output
                    address = request["endpoint"]
                    port = request["port"]
                    msg = OSC.OSCMessage("/" + settings_copy["name"])
                    msg.append(request["payloads"])

                    if not self._osc_client:
                        self._osc_client = OSC.OSCClient()
                        self._osc_client.connect((address, int(port)))

                    Util.send_osc(self._osc_client, msg)
                    api_call = None

                if api_call and self._debug == "true":
                    Util.log("RESTful response %s" % api_call)

                if "post_api_delay" in request:
                    time.sleep(float(request["post_api_delay"]))

        except Exception, exc:
            Util.log("Error firing an event for %s, event: %s" %
                     (self._settings["name"], str(exc)), "ERROR")
