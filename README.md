# lifelights
Control your home based on _any_ horizontal rectangles by using simple screenshots.

### 2 minute video
[![2 minute demo using Heroes of the Storm](http://img.youtube.com/vi/U1-Tj4fPKRE/0.jpg)](http://www.youtube.com/watch?v=U1-Tj4fPKRE "Heroes of the Storm + IoT")

### Requirements
- Microsoft Windows
- Python 2.7 [(link)](https://www.python.org/ftp/python/2.7/python-2.7.msi)

### First time installation
- Clone this repository to a directory on your machine [(how-to)](https://help.github.com/desktop/guides/contributing/cloning-a-repository-from-github-to-github-desktop/)
- Start > cmd > cd to the source code directory
- ```pip install -r requirements.txt```

### Usage
- Double click on 'lifelights.py' in Windows Explorer or run python lifelights.py from the command-line
- Enter the profile number when prompted
- Select the profile from the menu

### Known limitations
- Not compatible with OSX
- Game must be run as "windowed fullscreen" or "windowed"
- API POST requests will always be in JSON format
- OSC messages will be an array, not a dictionary, with the name of the field before the field value.

### Profile configuration details
Currently there is no input sanitation or verification, so drifting from the guidlines below will likely break the script.

- **window_title** (string): Title of the window that will be monitored
- **scan_interval** (float): Interval in seconds to take a screenshot
- **quadrant_capture_count** (integer): Number of quadrants to capture on the screen. Can be 1, 2, or 4. See "Final notes" section for details.
- **quadrant_number** (integer): Which quadrant to capture. See "Final notes" section for details.
- **watchers**: List of different 'watchers' to calculate. For example, if there was a green health bar and a blue mana bar, you would add a separate entry for both. To avoid wasting resources, this uses the same screenshot for each watcher listed. That is to say, there won't be another screenshot taken until all the watchers are processed.
  - **name** (string): Common name of what you are monitoring. Used for logging but can be anything that makes sense to you
  - **debug** (bool): true or false, displays the captured screen and a slider to set the blur amount
  - **change_threshold** (integer): Percentage (0-100) that determines when an API request should fire off. Prevents flooding the API endpoint with minor changes in health. For example, if this is set to 5, lights will only be updated on any 5% change to a health bar. 0 = don't throttle
  - **blur_amount** (integer): Amount of median blur to apply. Finds the median color of parts of an image -- useful for statuses who may not all be the same color.
  - **color_upper_limit**: Collection of R,G,B colors that sets the upper limit for the status bar to monitor. In layman's terms, "the lightest color the status bar will ever be".
  - **color_lower_limit**: Collection of R,G,B colors that sets the lower limit for the status bar to monitor. In layman's terms, "the darkest color the status bar will ever be".
  - *Take note*: The tighter you can set the color boundaries, the less false positives the script will detect. Tweak as needed.
  - **requests**: List of RESTful events or OSC messages that should be fired when the ```change_threshold``` is passed
    - **endpoint** (string): API endpoint
    - **method** (string): POST or GET for REST, OSC for OSC
    - **pre_api_delay** (float): Interval in seconds to sleep before sending the API request. Use 0.0 for no delay.
    - **post_api_delay** (float): Interval in seconds to sleep after sending the API request. Use 0.0 for no delay.
    - **payloads**: Collection of keys/values to send to the API endpoint. Currently supports the following special values:
      - *LIFELIGHT_RGB*: Array of an RGB color, calculated using the percentage to fade from green -> yellow -> red
      - *LIFELIGHT_RECT_WIDTH*: Integer of the current width of the status bar being monitored, in pixels
      - *LIFELIGHT_PERCENT*: Integer (0-100) of the status bar percentage
      - *LIFELIGHT_RAW_PERCENT*: Floating point (0-1) of the status bar percentage

### Final notes, thoughts and acknowledgements
- ```quadrant_capture_count``` and ```quadrant_number``` were implemented as a way to help save computer resources and prevent false positives. The reasoning behind it is, if a user only cares about the bottom left corner of the screen, why save the whole screen in memory and process it if we don't need to?
  - ```quadrant_capture_count``` can be either 1, 2 or 4. 1 tells the script that we only care about a single quadrant (top left, top right, bottom left, bottom right). 2 tells the script we care about 2 quadrants (either top or bottom). 4 is all 4 quadrants, or in other words, the entire screen.
  - ```quadrant_number``` should change depending on the value of ```quadrant_capture_count```.
    - If ```quadrant_capture_count = 1```, ```quadrant_number``` should be 1-4 (1 = top left, 2 = top right, 3 = bottom left, 4 = bottom right)
    - If ```quadrant_capture_count = 2```, ```quadrant_number``` should be 1-2 (1 = top half, 2 = bottom half)
    - ```quadrant_number``` is unused when ```quadrant_capture_count = 4``` (because it's the whole screen)
- The detection of rectanges is dynamic, but by design detection of the screen is not. If the game window is moved after launch, scanning may return no results.
- Try and find a good balance between ```scan_interval``` and ```change_threshold```, performance will be better and you won't slam the API endpoint.
- You will, of course, need an API endpoint to use. I am a contributor to [Home Assistant](https://home-assistant.io/), and a big fan. With that said, this script was designed with Home Assistant in mind, but can of course work with any API endpoint.
- The implementation would have been very different (ie: much worse) if it wasn't for [Adrian Rosebrock's article](http://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/) on tracking objects using Python.
- Thanks to all the authors of the libraries I used who are way smarter than me. [cv2](https://github.com/opencv/opencv/graphs/contributors), [pillow](https://github.com/python-pillow/Pillow/graphs/contributors), [numpy](https://github.com/numpy/numpy/graphs/contributors), [pyyaml](https://github.com/yaml/pyyaml/graphs/contributors), and [requests](https://github.com/kennethreitz/requests/graphs/contributors).

### FAQ (well, what I can imagine is going to be asked)
- Can I get banned for using this?
  - I don't know buddy, I'm not a wizard. From a technical standpoint, the script just takes a screenshot and does not read any memory from the game itself. So if screenshots are bannable, then probably, yes.
- You know what would be really cool is if you ...
  - Yes that would be cool. [I accept pull requests](https://help.github.com/articles/creating-a-pull-request/). I also accept Venmo if you can't write the feature yourself.
- Are there performance implications by using this?
  - I didn't see any, but your experience is going to based on your computer, and what configuration options used. You should not notice anything if you have an idle CPU core available, as the image processing runs single-threaded in a separate process.
- My 'xyz home autiomation component' isn't updating fast enough
  - Sorry about that, there isn't anything that can be done once the API request is fired off. You can see the time it was fired off in the output window of the script.
- Does it work with ... ?
  - As long as the game or application can be set to windowed mode, and as long as you are trying to measure the width of a rectangle, then yes, this should work just fine.
- How do I get the upper and lower bound colors?
  - Take a screenshot of your game, open in paint, color drop it, and find the RGB value. Move the saturaton slider up and down to get lighter and darker colors.

### To-do
- Add support for verticle rectangles
- Add ability to pass configuration file via command line
- Better configuration validation
- Cross platform support

### Process overview

![Detect health bar using RGB colors](http://i.imgur.com/rbIWEJr.png)

The image above shows a visible rectangle being drawn around the script detected rectange. You can uncomment lines 35, 46-50 in the WidthWatcher module to draw a similar rectangle for your application. Good for troubleshooting.

![Dynamically adjusts to the bar](http://i.imgur.com/ZVNUve9.png)

As your health (or mana, or anything) gets smaller, the invisible rectangle gets smaller. This updates at the ```scan_interval``` rate.

The script will then fire off the RESTful API calls based on the settings you define in the configuration file.

