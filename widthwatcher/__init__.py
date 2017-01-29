import requests as req
import json

from util import Util


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

        self._max_width = 0.0
        self._last_width = 0.0

        self.width = 0.0

    def scan(self, screen):
        """Scan an image and attempt to fit an invisible rectangle around a group of colors."""
        import cv2
        image_mask = cv2.inRange(screen, self._lower_bounds,
                                 self._upper_bounds)
        cnts = cv2.findContours(image_mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[-2]

        if len(cnts) > 0:
            max_cnt = max(cnts, key=cv2.contourArea)
            # x, y, w, h = cv2.boundingRect(c)
            _, _, width, _ = cv2.boundingRect(max_cnt)

            if (width - int(self._settings["min_width"])) >= 0:
                if self._max_width < width:
                    self._max_width = float(width)
                    Util.log("Max %s updated %d" %
                             (self._settings["name"], width))

                self.width = 1.0 * (float(width) / float(self._max_width))

            # uncomment for debugging purposes
            # cv2.rectangle(screen,(x,y),(x+w,y+h),(0,255,0),2)
            # cv2.imshow("bingo!", screen)
            # cv2.waitKey(0)
            # quit()

        else:
            self.width = 0.0

    def process(self):
        """Execute RESTful API calls based on the results of an image scan."""
        import copy

        if self.width == self._last_width:
            return

        percent = round(self.width * 100) / 100.0

        if percent + (self._settings["change_threshold"] * 1.0) > 1.0:
            # snap to 100%
            percent = 1.0
        elif percent - (self._settings["change_threshold"] * 1.0) < 0.0:
            # snap to 0%
            percent = 0.0

        if abs(self._last_width - self.width) < (self._settings["change_threshold"] * 1.0) / 100 \
                and 0.0 < percent < 1.0:
            return

        if percent <= 0.0:
            Util.log("%s reached 0.0 -- did you die? :P" %
                     self._settings["name"])
        else:
            Util.log("%s updated to %.2f" % (self._settings["name"], percent))

        try:
            self._last_width = self.width
            rgb = [
                int(255 * (100 - (percent * 100)) / 100),
                int(255 * (percent * 100) / 100), 0
            ]

            settings_copy = copy.deepcopy(self._settings)

            for index, request in enumerate(settings_copy["requests"]):
                for payload, value in request["payloads"].items():
                    if value == "RGB_PLACEHOLDER":
                        settings_copy["requests"][index]["payloads"][
                            payload] = rgb
                    if value == "WIDTH_PLACEHOLDER":
                        settings_copy["requests"][index]["payloads"][
                            payload] = int(self.width)
                    if value == "PERCENT_PLACEHOLDER":
                        settings_copy["requests"][index]["payloads"][
                            payload] = int((percent * 100))
                    if value == "BRIGHTNESS_PLACEHOLDER":
                        settings_copy["requests"][index]["payloads"][
                            payload] = int((percent * 255))

                if request["method"].upper() == "POST":
                    api_call = req.post(
                        request["endpoint"],
                        data=json.dumps(request["payloads"]))
                if request["method"].upper() == "GET":
                    api_call = req.get(
                        request["endpoint"],
                        data=request["payloads"])

                if api_call:
                    Util.log("RESTful response %s" % api_call)

        except Exception, exc:
            Util.log("Error firing an event for %s, event: %s" %
                     (self._settings["name"], exc))
