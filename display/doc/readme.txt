Requirements:

- uzbl browser (sudo apt-get install uzbl)
- matchbox_window_manager (sudo apt-get install matchbox-window-manager)
- xinit (sudo apt-get install xinit)
- sh v 1.11 (sudo pip install sh)

To test the viewer in the regular desktop environment, you can just run:

$ python demo.py

To test in fullsreen mode, do the following:

1) Create a startup script (e.g. start.sh):

#!/bin/bash
python demo.py & matchbox-window-manager -use_titlebar no -use_cursor no

2) Run xinit with startup script:

$ xinit ./start.sh
