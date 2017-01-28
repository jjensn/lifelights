# lifelights
Color your RGB bulbs based on *any* in-game status bars. 

Current configuration is for Heroes of the Storm health, but can be made to fit any game and any horizontal bar!

![Detect health bar using RGB colors](http://i.imgur.com/rbIWEJr.png)

Attempt to detect a health bar in game, and measure the width of the rectangle to get current status

![Dynamically adjusts to the bar](http://i.imgur.com/ZVNUve9.png)

As your health (or mana, or anything) gets smaller, the invisible rectangle gets smaller.

The script will then fire off a RESTful API call based on the settings you define in the configuration file.

