# lifelights
Control your home based on _any_ horizontal status bars by using simple screenshots.

### Requirements
- Microsoft Windows
- Python 2.7 [(link)](https://www.python.org/ftp/python/2.7/python-2.7.msi)

### First time installation
- Clone this repository to a directory on your machine [(how-to)](https://help.github.com/desktop/guides/contributing/cloning-a-repository-from-github-to-github-desktop/)
- Start > cmd > cd to the source code directory
- ```pip install -r requirements.txt```

### Usage
- Double click on 'lifelights.py' in Windows Explorer or run python lifelights.py from the command-line

### Known limitations
- Not compatible with OSX
- Game must be run as "windowed fullscreen" or "windowed"
- API POST requests will always be in JSON format

### Configuration details
Currently there is no input sanitation or verification, so drifting from the guidlines below will likely break the script.

- **window_title** (string): Title of the window that will be monitored
- **scan_interval** (float): Interval in seconds to take a screenshot
- **watchers**: List of different 'watchers' to calculate. For example, if there was a green health bar and a blue mana bar, you would add a separate entry for both. To avoid wasting resources, this uses the same screenshot for each watcher listed. That is to say, there won't be another screenshot taken until all the watchers are processed.
  - **name** (string): Common name of what you are monitoring. Used for logging but can be anything that makes sense to you
  - **min_width** (integer): Minimum number of pixels (width) of a horizontal bar (rectangle) needed to be considered a status bar. Helps prevent false positives for elements on the screen that are the same color as the status bar being monitored.
  - **change_threshold** (integer): Percentage (0-100) that determines when an API request should fire off. Prevents flooding the API endpoint with minor changes in health. For example, if this is set to 5, lights will only be updated on any 5% change to a health bar. 0 = don't throttle
  - **color_upper_limit**: Collection of R,G,B colors that sets the upper limit for the status bar to monitor. In layman's terms, "the lightest color the status bar will ever be".
  - **color_lower_limit**: Collection of R,G,B colors that sets the lower limit for the status bar to monitor. In layman's terms, "the darkest color the status bar will ever be".
  - **requests**: List of RESTful events that should be fired when the ```change_threshold``` is passed
    - **endpoint** (string): API endpoint
    - **method** (string): POST or GET
    - **payloads**: Collection of keys/values to send to the API endpoint. Currently supports the following special values:
      - *RGB_PLACEHOLDER*: Array of an RGB color, calculated using the percentage to fade from green -> yellow -> red
      - *WIDTH_PLACEHOLDER*: Integer of the current width of the status bar being monitored, in pixels
      - *PERCENT_PLACEHOLDER*: Integer (0-100) of the status bar percentage
      - *BRIGHTNESS_PLACEHOLDER*: Integer (0-255) of the status bar percentage


### Final notes, thoughts and acknowledgements
- The detection of rectanges is dynamic, but by design detection of the screen is not. If the game window is moved after launch, scanning may return no results.
- The tighter you can set the color boundaries, the less false positives the script will detect. Tweak as needed.
- Try and find a good balance between ```scan_interval``` and ```change_threshold```, performance will be better and you won't slam the API endpoint.
- You will, of course, need an API endpoint to use. I am a contributor to [Home Assistant](https://home-assistant.io/), and a big fan. With that said, this script was designed with Home Assistant in mind, but can of course work with any API endpoint.
- The implementation would have been very different (ie: much worse) if it wasn't for [Adrian Rosebrock's article](http://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/) on tracking objects using Python.
- Thanks to all the authors of the libraries I used who are way smarter than me. [cv2](https://github.com/opencv/opencv/graphs/contributors), [pillow](https://github.com/python-pillow/Pillow/graphs/contributors), [numpy](https://github.com/numpy/numpy/graphs/contributors), [pyyaml](https://github.com/yaml/pyyaml/graphs/contributors), and [requests](https://github.com/kennethreitz/requests/graphs/contributors).

### FAQ (well, what I can imagine is going to be asked)
- Can I get banned for using this?
  - I don't know buddy, I'm not a wizard. From a technical standpoint, the script just takes a screenshot. So if screenshots are bannable, then probably, yes.
- You know what would be really cool is if you ...
  - Yes that would be cool. [I accept pull requests](https://help.github.com/articles/creating-a-pull-request/). I also accept Venmo if you can't write the feature yourself.
- Are there performance implications by using this?
  - I didn't see any, but your experience is going to based on your computer, and what configuration options used.
- My 'xyz home autiomation component' isn't updating fast enough
  - Sorry about that, there isn't anything that can be done once the API request is fired off. You can see the time it was fired off in the output window of the script.
- How do I get the upper and lower bound colors?
  - Take a screenshot of your game, open in paint, color drop it, and find the RGB value. Move the saturaton slider up and down to get lighter and darker colors.

### Todo
- Add support for verticle rectanges
- Add ability to pass configuration file via command line
- Configuration validation
- Cross platform support
- Add configuration option to specify a specified screne quadrant

### Process overview

![Detect health bar using RGB colors](http://i.imgur.com/rbIWEJr.png)

The image above shows a visible rectangle being drawn around the scripts detected rectange. You can uncomment lines 35, 46-50 in the WidthWatcher module to draw a similar rectangle for your application. Good for troubleshooting.

![Dynamically adjusts to the bar](http://i.imgur.com/ZVNUve9.png)

As your health (or mana, or anything) gets smaller, the invisible rectangle gets smaller. This updates at the ```scan_interval``` rate.

The script will then fire off the RESTful API calls based on the settings you define in the configuration file.

