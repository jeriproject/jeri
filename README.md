# JeRI

## Python setup

Python (along with a bunch of Python packages) is needed to run the main program.

1. Install Python 2.7 ([Link](https://www.python.org/download/releases/2.7.2/))
2. Install the Python package manager
```
$ sudo easy_install pip
```
3. Install the Python dependencies
```
$ sudo pip install -r requirements.txt
```

## Java setup

Java is needed to train and apply the NE classifier model.

1. Install Java SE Runtime Environment 8 
   ([Link](http://www.oracle.com/technetwork/java/javase/downloads/jre8-downloads-2133155.html))

## Using the program

Once the required dependencies are installed, run the GUI with
```
$ python jeri-gui.py
```

1. Click on "Train model" to use the annotated training data in the "annotated" folder to create an NE classifier model, which is then saved to the "models" folder
2. Click on "Select model" to select a classifier model file
3. Click on "Select text" to select a text file you want to do NE classification on; the example "frankentext.txt" is included
4. Click on "Classify model" to tag the text file with categories
