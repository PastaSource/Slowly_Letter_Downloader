# Slowly Letter Downloader

Automates the process of downloading letters from slowly in PDF form.

## Installation

A Windows binary executable is currently in development.

## Requirements

 - Python 3.9
 - Selenium==4.20
 - cefpython3==66.1
 - py7zr==0.20.0
 - pdfrw==0.4
 - customtkinter==4.5.10
 - pyglet==1.5.26

A Windows binary executable is currently in development.

## Features

 **Current features**
 - Graphical user interface for ease of use
 - Download letters from as many penpals as you want as PDFs
 - Download images attached to letters, including stamps used
 - Can be run again in the future to download new letters received/sent (currently for this feature to work, you cannot move the letters from where the program places them)
 - Almost completely automatic

**Planned features** 

 - Allow for customisation of PDFs downloaded e.g. portrait, landscape
 - Both light and dark themes selectable by the user
 - Use the user installed version of Chrome if available so no Chrome download within the app is required

## Usage

This program can only be used via the GUI, you can launch it using:
```python
python main.py
```
If you're using the Windows executable, just open main.exe.

 - Once opened scan the QR code from the integrated browser using the Slowly app on your phone, and click "Load Penpals".
 - If this is your first time launching the program you will have to wait whilst it downloads Chrome, this may take a while depending on your internet connection.
 - When your penpals have loaded, select the ones you wish to download the letters from and click the "Run" button.
 - Downloaded letters can be found within the root directory, alongside the main.exe file, in a folder called "Letters".


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
