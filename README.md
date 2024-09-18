# AirRec
AirRec is a program to aid in developing aircraft recognition skills.\
It takes aircraft from a txt list, and creates customizable slideshows using images it downloads.\
Supports custom txt lists in the custom mode.

# How to use
Download AirRec.exe and Default.txt from the latest release in versions, and place them into the same folder. \
Run AirRec.exe as needed and add more .txt files as required.

# Controls
Backspace to got to the previous slide. \
Enter to go to the next slide. \
Esc to close the slideshow.

# Versions
https://github.com/Thespacemanfil/Air-Rec-Program/releases/tag/v1.0

# Dependencies
random\
os\
glob\
Pillow (PIL)\
bing_image_downloader\
tkinter

## Creating an executable
pyinstaller --onefile --console AirRec.py\
python -m PyInstaller --onefile --console AirRec.py
