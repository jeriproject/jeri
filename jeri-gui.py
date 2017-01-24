#!/usr/bin/python

"""
The top-level GUI.
"""

import os
import Tkinter as tk
import ttk

import jeri.constants as const
from jeri.gui.analysis import JeriAnalysis
#from jeri.gui.annotator import JeriAnnotator

ROOT_TITLE = "JERI"
ROOT_WIDTH = 1000
ROOT_HEIGHT = 800
ROOT_POS_X = 100
ROOT_POS_Y = 100

def main():
    for d in (const.PROP_DIR, const.MODELS_DIR, const.ALC_DIR, const.CAL_DIR):
        if not os.path.exists(d):
            os.mkdir(d)
            print("Created directory: {}".format(d))

    root = tk.Tk()
    root.title("JeRI")
    root.geometry("{}x{}+{}+{}".format(ROOT_WIDTH, ROOT_HEIGHT, ROOT_POS_X, ROOT_POS_Y))
    root.columnconfigure(0, weight=1)
    gui = JeriMain(root)
    gui.pack(fill=tk.BOTH, expand=tk.TRUE)
    root.mainloop()

class JeriMain(ttk.Notebook):
    def __init__(self, parent, logfile="jeri-gui_log.txt"):
        ttk.Notebook.__init__(self, parent)
        self.parent = parent
        self.logfile = logfile

        analysis = JeriAnalysis(self)
        self.add(analysis, text="Analysis")

        #annotator = JeriAnnotator(self)
        #self.add(annotator, text="Annotator")

    def write_to_log(self, msg):
        with open(self.logfile, 'a') as outfile:
            outfile.write(msg)

if __name__ == '__main__':
    main()
