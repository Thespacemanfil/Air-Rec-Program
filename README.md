# AirRec
AirRec is a program to aid in developing aircraft recognition skills.\
It takes aircraft from a txt list, and creates customizable slideshows using images it downloads.\
Supports custom txt lists in the custom mode.

# Versions
https://github.com/Thespacemanfil/Air-Rec-Program/releases/tag/v1.1
https://github.com/Thespacemanfil/Air-Rec-Program/releases/tag/stable

# Dependencies
random\
os\
glob\
Pillow (PIL)\
bing_image_downloader\
tkinter

## Creating an executable
pyinstaller --onefile --console AirRec.py\
python -m nuitka --follow-imports AirRec.py\
python -m nuitka --follow-imports --deployment --enable-plugin=tk-inter AirRec.py