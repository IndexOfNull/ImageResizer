
██╗███╗░░░███╗░█████╗░░██████╗░███████╗  ██████╗░███████╗░██████╗██╗███████╗███████╗██████╗░
██║████╗░████║██╔══██╗██╔════╝░██╔════╝  ██╔══██╗██╔════╝██╔════╝██║╚════██║██╔════╝██╔══██╗
██║██╔████╔██║███████║██║░░██╗░█████╗░░  ██████╔╝█████╗░░╚█████╗░██║░░███╔═╝█████╗░░██████╔╝
██║██║╚██╔╝██║██╔══██║██║░░╚██╗██╔══╝░░  ██╔══██╗██╔══╝░░░╚═══██╗██║██╔══╝░░██╔══╝░░██╔══██╗
██║██║░╚═╝░██║██║░░██║╚██████╔╝███████╗  ██║░░██║███████╗██████╔╝██║███████╗███████╗██║░░██║
╚═╝╚═╝░░░░░╚═╝╚═╝░░╚═╝░╚═════╝░╚══════╝  ╚═╝░░╚═╝╚══════╝╚═════╝░╚═╝╚══════╝╚══════╝╚═╝░░╚═╝


A simple python script for resizing images to meet a target file size. Running the program on a folder will resize every image in the folder and its subfolders (recursively). It resizes each image in-place, so there's no need to modify your names or folder organization. Your folder can have non-image files; any files that are not `.png`, `.jpg`, `.jpeg` will be ignored.

***Since this program overwrites files, be sure to make a backup before running it!***

--- Usage ---

There are a few ways to use the script depending on your use case. 

* Drag and Drop/Double Click (easiest)

    You can drag and drop entire folders onto the .exe/.py file. Double clicking the .exe/.py file to run it also works.

    **Note**: This only works if you've compiled a binary or your system is configured to allow running .py files.

* Interactive Usage

    The easiest way to run the script is to simply run
    ```sh
    python3 main.py
    ```
    You will be prompted for all the necessary parameters. It will still modify files in-place, so be careful!

* Non-Interactive Usage

    You can run the script non-interactively be specifying all the necessary command parameters:
    ```sh
    python3 main.py --size 1 --iter 5 -y img_dir
    ```
    (`--size 1` indicates one megabyte, `--iter 5` tries five resizes on each image, and `-y` bypasses the safety prompt telling you to back your files up)

