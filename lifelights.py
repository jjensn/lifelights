import time
import sys
import os
import itertools
from util import Util
from widthwatcher import WidthWatcher
import yaml

sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))


def main():
    """Main entrypoint for script."""
    config_file = open('lifelights.yml')
    settings = yaml.safe_load(config_file)
    config_file.close()

    spinner = itertools.cycle(['-', '/', '|', '\\'])

    watcher_list = [WidthWatcher(w) for w in settings["watchers"]]

    window = Util.find_window_by_title(settings["window_title"])

    while True:

        if window is None:
            sys.stdout.write("Waiting for window ... " + spinner.next() + "\r")
            sys.stdout.flush()
            window = Util.find_window_by_title(settings["window_title"])
            #sys.stdout.write('\b')
            time.sleep(0.3)
            continue

        time.sleep(float(settings["scan_interval"]))

        screen = Util.screenshot(window)

        if not screen.any():
            continue

        for watch in watcher_list:
            watch.scan(screen)
            watch.process()


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print "Goodbye, hero."
