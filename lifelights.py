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
    profiles = next(os.walk('profiles'))[2]

    if len(profiles) == 0:
        print "Unable to locate any game profiles in the profiles directory"
        sys.exit()

    for index, profile in enumerate(profiles):
        # Use the filename as the name of the profile
        print "%d - %s" % (index+1, profile.replace("_", " ").rsplit('.', 1)[0].title())

    profile_id = int(input('Enter the profile number to load: ')) - 1

    if profile_id > len(profiles) or profile_id < 0:
        print "Profile number out of range, must be between 1 and %d" % len(profiles)
        sys.exit()

    config_file = open("profiles/%s" % profiles[profile_id])
    settings = yaml.safe_load(config_file)
    config_file.close()

    config_error = Util.has_valid_config(settings)

    if config_error:
        Util.log("Error found in configuration file -- %s" % config_error)
        sys.exit()

    spinner = itertools.cycle(['-', '/', '|', '\\'])

    watcher_list = [WidthWatcher(w) for w in settings["watchers"]]

    window = Util.find_window_by_title(settings["window_title"])

    if window is not None:
        window = Util.resize_capture_area(window, settings)

    while True:

        if window is None:
            sys.stdout.write("Waiting for window ... " + spinner.next() + "\r")
            sys.stdout.flush()
            window = Util.find_window_by_title(settings["window_title"])
            if window is not None:
                window = Util.resize_capture_area(window, settings)
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
