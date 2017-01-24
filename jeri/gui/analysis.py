"""
The analysis window.

Performs various functions with AlchemyAPI, OpenCalais and Stanford NER.
"""

import datetime
import glob
import json
import os
import subprocess
import Tkinter as tk
import tkFileDialog
import time

import jeri.constants as const
from jeri.pipeline import alchemy_tools as alc
from jeri.pipeline import calais_tools as cal

class JeriAnalysis(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        parent.write_to_log("==== START ANALYSIS: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.columnconfigure(0, weight=1)

        # Text window
        self.output_text = self.make_text_frame()

        # General frame
        self.text_filepath = self.make_general_frame()

        # Stanford NER frame
        self.annot_count, self.model_filepath, self.tagged_filepath, self.tagged_file_display = self.make_stanford_frame()

        #==== AlchemyAPI + OpenCalais frame
        alchemy_calais_frame = self.make_alchemy_calais_frame()

        # AlchemyAPI frame
        self.alchemy_entities_obtained_yesno, self.alchemy_relations_obtained_yesno, self.alchemy_entities_obtained_display, self.alchemy_relations_obtained_display = self.make_alchemy_frame(alchemy_calais_frame)

        # OpenCalais frame
        self.calais_results_obtained_yesno, self.calais_results_obtained_display = self.make_calais_frame(alchemy_calais_frame)
        #====

        # Combined frame
        self.make_combined_frame()

        #==== Data

        self.attributed_entiites = []

    def __del__(self):
        parent.write_to_log("==== END: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    #==== Widgets

    def make_text_frame(self):
        text_frame = tk.Frame(self)
        text_frame.grid(row=0, column=0, sticky=tk.NSEW)
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        text_frame.columnconfigure(1, weight=0)

        output_text = tk.Text(text_frame)
        output_text.grid(row=0, column=0, sticky=tk.NSEW)
        output_text_scrollbar = tk.Scrollbar(text_frame)
        output_text_scrollbar.grid(row=0, column=1, sticky=tk.NSEW)

        output_text_scrollbar.config(command=output_text.yview)
        output_text.config(yscrollcommand=output_text_scrollbar.set)

        return output_text

    def make_general_frame(self):
        text_file = tk.StringVar()
        text_file.set("(No file selected)")

        general_frame = tk.Frame(self)
        general_frame.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, pady=(0, 20))
        general_frame.rowconfigure(0, weight=1)
        general_frame.rowconfigure(1, weight=1)
        general_frame.columnconfigure(0, weight=0)
        general_frame.columnconfigure(1, weight=1)
        general_frame.columnconfigure(2, weight=0)

        # Row 0
        general_header = tk.Label(general_frame, text="General", bg="#E1E0B4")
        general_header.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW)

        # Row 1
        text_file_label = tk.Label(general_frame, text="Selected text file:", bg="#DDE4CD")
        text_file_label.grid(row=1, column=0, sticky=tk.NSEW)
        text_file_display = tk.Label(general_frame, textvariable=text_file, anchor=tk.W)
        text_file_display.grid(row=1, column=1, sticky=tk.NSEW)
        select_text_button = tk.Button(general_frame, text="Browse", command=self.select_text)
        select_text_button.grid(row=1, column=2, sticky=tk.NSEW)

        return text_file

    def make_stanford_frame(self):
        annot_count = tk.IntVar()
        annot_count.set(self.stanford_count_annotated_files())
        model_file = tk.StringVar()
        model_file.set("(No file selected)")
        tagged_file = tk.StringVar()
        tagged_file.set("(No file selected)")

        stanford_frame = tk.Frame(self)
        stanford_frame.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, pady=(0, 20))
        stanford_frame.rowconfigure(0, weight=1)
        stanford_frame.rowconfigure(1, weight=1)
        stanford_frame.rowconfigure(2, weight=1)
        stanford_frame.rowconfigure(3, weight=1)
        stanford_frame.rowconfigure(4, weight=1)
        stanford_frame.rowconfigure(5, weight=1)
        stanford_frame.rowconfigure(6, weight=1)
        stanford_frame.columnconfigure(0, weight=0)
        stanford_frame.columnconfigure(1, weight=1)
        stanford_frame.columnconfigure(2, weight=0)

        # Row 0
        stanford_header = tk.Label(stanford_frame, text="Stanford NER", bg="#E6649C")
        stanford_header.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW)

        # Row 1
        annot_count_label_display_frame = tk.Frame(stanford_frame)
        annot_count_label_display_frame.grid(row=1, column=0)
        annot_count_label = tk.Label(annot_count_label_display_frame, text="No. of annotated files:", bg="#DDE4CD")
        annot_count_label.grid(row=0, column=0, sticky=tk.NSEW)
        annot_count_display = tk.Label(annot_count_label_display_frame, textvariable=annot_count, anchor=tk.W)
        annot_count_display.grid(row=0, column=1, sticky=tk.NSEW)
        annot_count_path_frame = tk.Frame(stanford_frame)
        annot_count_path_frame.grid(row=1, column=1)
        annot_count_path_label = tk.Label(annot_count_path_frame, text="Folder:", bg="#DDE4CD")
        annot_count_path_label.grid(row=0, column=0, sticky=tk.NSEW)
        annot_count_path_display = tk.Label(annot_count_path_frame, text=os.path.abspath(const.ANNOTATED_DIR), anchor=tk.W)
        annot_count_path_display.grid(row=0, column=1, sticky=tk.NSEW)
        annot_count_refresh_button = tk.Button(stanford_frame, text="Refresh", command=self.stanford_refresh_annot_count)
        annot_count_refresh_button.grid(row=1, column=2, sticky=tk.NSEW)

        # Row 2
        train_button = tk.Button(stanford_frame, text="Train model", command=self.stanford_train)
        train_button.grid(row=2, column=0, columnspan=3, sticky=tk.NSEW)

        # Row 3
        model_file_label = tk.Label(stanford_frame, text="Selected model file:", bg="#DDE4CD")
        model_file_label.grid(row=3, column=0, sticky=tk.NSEW)
        model_file_display = tk.Label(stanford_frame, textvariable=model_file, anchor=tk.W)
        model_file_display.grid(row=3, column=1, sticky=tk.NSEW)
        select_model_button = tk.Button(stanford_frame, text="Browse", command=self.stanford_select_model)
        select_model_button.grid(row=3, column=2, sticky=tk.NSEW)

        # Row 4
        classify_button = tk.Button(stanford_frame, text="Classify text", command=self.stanford_classify)
        classify_button.grid(row=4, column=0, columnspan=3, sticky=tk.NSEW)

        # Row 5
        tagged_file_label = tk.Label(stanford_frame, text="Selected tagged file:", bg="#DDE4CD")
        tagged_file_label.grid(row=5, column=0, sticky=tk.NSEW)
        tagged_file_display = tk.Label(stanford_frame, textvariable=tagged_file, anchor=tk.W)
        tagged_file_display.grid(row=5, column=1, sticky=tk.NSEW)
        select_tagged_button = tk.Button(stanford_frame, text="Browse", command=self.stanford_select_tagged)
        select_tagged_button.grid(row=5, column=2, sticky=tk.NSEW)

        # Row 6
        list_entities_button = tk.Button(stanford_frame, text="List entities", command=self.stanford_list_entities)
        list_entities_button.grid(row=6, column=0, columnspan=3, sticky=tk.NSEW)

        return annot_count, model_file, tagged_file, tagged_file_display

    def make_alchemy_calais_frame(self):
        alchemy_calais_frame = tk.Frame(self)
        alchemy_calais_frame.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW, pady=(0, 20))
        alchemy_calais_frame.rowconfigure(0, weight=1)
        alchemy_calais_frame.columnconfigure(0, weight=1)
        alchemy_calais_frame.columnconfigure(1, weight=1)

        return alchemy_calais_frame

    def make_alchemy_frame(self, alchemy_calais_frame):
        alchemy_entities_obtained_yesno = tk.StringVar()
        alchemy_entities_obtained_yesno.set("N/A")
        alchemy_relations_obtained_yesno = tk.StringVar()
        alchemy_relations_obtained_yesno.set("N/A")

        alchemy_frame = tk.Frame(alchemy_calais_frame)
        alchemy_frame.grid(row=0, column=0, sticky=tk.NSEW)
        alchemy_frame.rowconfigure(0, weight=1)
        alchemy_frame.rowconfigure(1, weight=1)
        alchemy_frame.rowconfigure(2, weight=1)
        alchemy_frame.rowconfigure(3, weight=1)
        alchemy_frame.rowconfigure(4, weight=1)
        alchemy_frame.columnconfigure(0, weight=1)
        alchemy_frame.columnconfigure(1, weight=1)

        # Row 0
        alchemy_header = tk.Label(alchemy_frame, text="AlchemyAPI", bg="#AF46E6")
        alchemy_header.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)

        # Row 1
        alchemy_entities_obtained_label = tk.Label(alchemy_frame, text="Entities obtained?", bg="#DDE4CD")
        alchemy_entities_obtained_label.grid(row=1, column=0, sticky=tk.NSEW)
        alchemy_entities_obtained_display = tk.Label(alchemy_frame, textvariable=alchemy_entities_obtained_yesno)
        alchemy_entities_obtained_display.grid(row=1, column=1, sticky=tk.NSEW)

        # Row 2
        alchemy_relations_obtained_label = tk.Label(alchemy_frame, text="Relations obtained?", bg="#DDE4CD")
        alchemy_relations_obtained_label.grid(row=2, column=0, sticky=tk.NSEW)
        alchemy_relations_obtained_display = tk.Label(alchemy_frame, textvariable=alchemy_relations_obtained_yesno)
        alchemy_relations_obtained_display.grid(row=2, column=1, sticky=tk.NSEW)

        # Row 3
        alchemy_get_results_button = tk.Button(alchemy_frame, text="Get API results", command=self.alchemy_get_results_to_file)
        alchemy_get_results_button.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW)

        # Row 4
        alchemy_list_all_entities_button = tk.Button(alchemy_frame, text="List all entities", command=self.alchemy_list_all_entities)
        alchemy_list_all_entities_button.grid(row=4, column=0, sticky=tk.NSEW)
        alchemy_list_attr_entities_button = tk.Button(alchemy_frame, text="List attributed entities", command=self.alchemy_list_attributed_entities)
        alchemy_list_attr_entities_button.grid(row=4, column=1, sticky=tk.NSEW)

        return alchemy_entities_obtained_yesno, alchemy_relations_obtained_yesno, alchemy_entities_obtained_display, alchemy_relations_obtained_display

    def make_calais_frame(self, alchemy_calais_frame):
        calais_results_obtained_yesno = tk.StringVar()
        calais_results_obtained_yesno.set("N/A")

        calais_frame = tk.Frame(alchemy_calais_frame)
        calais_frame.grid(row=0, column=1, sticky=tk.NSEW)
        calais_frame.rowconfigure(0, weight=1)
        calais_frame.rowconfigure(1, weight=1)
        calais_frame.rowconfigure(2, weight=1)
        calais_frame.rowconfigure(3, weight=1)
        calais_frame.rowconfigure(4, weight=1)
        calais_frame.columnconfigure(0, weight=1)
        calais_frame.columnconfigure(1, weight=1)

        # Row 0
        calais_header = tk.Label(calais_frame, text="OpenCalais", bg="#5628E8")
        calais_header.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)

        # Row 1
        calais_results_obtained_label = tk.Label(calais_frame, text="Results obtained?", bg="#DDE4CD")
        calais_results_obtained_label.grid(row=1, column=0, sticky=tk.NSEW)
        calais_results_obtained_display = tk.Label(calais_frame, textvariable=calais_results_obtained_yesno)
        calais_results_obtained_display.grid(row=1, column=1, sticky=tk.NSEW)

        # Row 2
        calais_blank_row = tk.Label(calais_frame, text="")
        calais_blank_row.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW)

        # Row 3
        calais_get_results_button = tk.Button(calais_frame, text="Get API results", command=self.calais_get_results_to_file)
        calais_get_results_button.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW)

        # Row 4
        calais_list_all_entities_button = tk.Button(calais_frame, text="List all entities", command=self.calais_list_all_entities)
        calais_list_all_entities_button.grid(row=4, column=0, sticky=tk.NSEW)
        calais_list_attr_entities_button = tk.Button(calais_frame, text="List attributed entities", command=self.calais_list_attributed_entities)
        calais_list_attr_entities_button.grid(row=4, column=1, sticky=tk.NSEW)

        return calais_results_obtained_yesno, calais_results_obtained_display

    def make_combined_frame(self):
        combined_frame = tk.Frame(self)
        combined_frame.grid(row=4, column=0, sticky=tk.NSEW)
        combined_frame.rowconfigure(0, weight=1)
        combined_frame.rowconfigure(1, weight=1)
        combined_frame.rowconfigure(2, weight=1)
        combined_frame.columnconfigure(0, weight=1)

        # Row 0
        combined_header = tk.Label(combined_frame, text="Combined", bg="#E1E0B4")
        combined_header.grid(row=0, column=0, sticky=tk.NSEW)

        # Row 1
        cross_ref_button = tk.Button(combined_frame, text="Cross-reference Stanford NER and AlchemyAPI results", command=self.combined_cross_ref_stanford_alchemy)
        cross_ref_button.grid(row=1, column=0, sticky=tk.NSEW)

        # Row 2
        compile_attr_button = tk.Button(combined_frame, text="Compile attributed entities", command=self.combined_compile_attributed_entities)
        compile_attr_button.grid(row=2, column=0, sticky=tk.NSEW)

        return

    #======== Callbacks

    #==== General

    def select_text(self):
        file_opts = {
            'defaultextension': const.TEXT_EXTENSION,
            'filetypes': [("Text files", const.TEXT_EXTENSION), ("All files", ".*")],
            'initialdir': ".",
            'parent': self,
        }

        text_filepath = tkFileDialog.askopenfilename(**file_opts)
        if text_filepath:
            self.text_filepath.set(text_filepath)
            self.print_msg_to_stdout_and_gui("Text file {0} selected".format(text_filepath))
            self.alchemy_update_entities_obtained(self.text_filepath.get())
            self.alchemy_update_relations_obtained(self.text_filepath.get())
            self.calais_update_results_obtained(self.text_filepath.get())

    #==== Stanford NER

    def stanford_refresh_annot_count(self):
        annot_count = self.stanford_count_annotated_files()
        self.annot_count.set(annot_count)
        self.update()
        self.print_msg_to_stdout_and_gui("{} annotated files detected".format(annot_count))

    def stanford_select_model(self):
        file_opts = {
            'defaultextension': const.MODEL_EXTENSION,
            'filetypes': [("Model files", const.MODEL_EXTENSION), ("All files", ".*")],
            'initialdir': os.path.join(".", "models"),
            'parent': self,
        }

        model_filepath = tkFileDialog.askopenfilename(**file_opts)
        if model_filepath:
            self.model_filepath.set(model_filepath)
            self.print_msg_to_stdout_and_gui("Model file {0} selected".format(model_filepath))

    def stanford_select_tagged(self):
        file_opts = {
            'defaultextension': const.TAGGED_EXTENSION,
            'filetypes': [("Tagged files", const.TAGGED_EXTENSION), ("All files", ".*")],
            'initialdir': ".",
            'parent': self,
        }

        tagged_filepath = tkFileDialog.askopenfilename(**file_opts)
        if tagged_filepath:
            self.tagged_filepath.set(tagged_filepath)
            self.print_msg_to_stdout_and_gui("Tagged file {0} selected".format(tagged_filepath))

    def stanford_train(self):
        annot_filepaths = glob.glob(os.path.join(const.ANNOTATED_DIR, const.ANNOT_GLOB_PATTERN))
        if os.name == 'nt':
            annot_filepaths = [annot_filepath.replace("\\", "/") for annot_filepath in annot_filepaths]
        if len(annot_filepaths) == 0:
            self.print_msg_to_stdout_and_gui("No annotated files found; aborting...")
            return
        self.print_msg_to_stdout_and_gui("{0} annotated files found".format(len(annot_filepaths)))

        self.print_msg_to_stdout_and_gui("Generating config file...")
        prop_filepath, serialize_filepath = self.stanford_generate_prop_config(annot_filepaths)
        self.print_msg_to_stdout_and_gui("Config file written to {0}".format(prop_filepath))

        self.print_msg_to_stdout_and_gui("Training model...")

        t_start = time.time()

        p_create_model = self.stanford_create_model(prop_filepath)
        output, error = p_create_model.communicate()
        if p_create_model.returncode != 0:
            self.print_msg_to_stdout_and_gui(output.strip())
            self.print_msg_to_stdout_and_gui("Unable to train model")
            return

        t_end = time.time()
        t_elapsed_sec = t_end - t_start
        t_elapsed_hms = time.strftime("%H:%M:%S", time.gmtime(t_elapsed_sec))
        self.print_msg_to_stdout_and_gui("Completed in {0}".format(t_elapsed_hms))

        self.print_msg_to_stdout_and_gui("Model written to {0}".format(serialize_filepath))

    def stanford_classify(self):
        if self.model_filepath.get() == "(No file selected)":
            self.print_msg_to_stdout_and_gui("No model file selected; cannot perform classification")
            return

        if self.text_filepath.get() == "(No file selected)":
            self.print_msg_to_stdout_and_gui("No text file selected; cannot perform classification")
            return

        self.print_msg_to_stdout_and_gui("Classifying text entities...")
        t_start = time.time()
        p_classify_text, tagged_filepath = self.stanford_classify_text(self.model_filepath.get(), self.text_filepath.get())
        output, error = p_classify_text.communicate()
        if p_classify_text.returncode != 0:
            self.print_msg_to_stdout_and_gui("Unable to classify text")
            return
        t_end = time.time()
        t_elapsed_sec = t_end - t_start
        t_elapsed_hms = time.strftime("%H:%M:%S", time.gmtime(t_elapsed_sec))
        self.print_msg_to_stdout_and_gui("Completed in {0}".format(t_elapsed_hms))

        self.print_msg_to_stdout_and_gui("Tagged file written to {0}".format(tagged_filepath))

    def stanford_list_entities(self):
        if self.tagged_filepath.get() == "(No file selected)":
            self.print_msg_to_stdout_and_gui("No tagged file selected; cannot list entities")
            return

        tagged_tokens = self.stanford_get_tagged_lines(self.tagged_filepath.get())
        entities = self.stanford_get_tagged_entities(tagged_tokens)
        pad = max([len(entity[0]) for entity in entities]) + 1
        self.print_msg_to_stdout_and_gui("==== ENTITIES " + "=" * (pad - 14 + 6))
        for entity in entities:
            name, label = entity
            line = name
            line += " " * (pad - len(name))
            line += "-> " + label
            self.print_msg_to_stdout_and_gui(line)
        self.print_msg_to_stdout_and_gui("=" * (pad + 6))

    #==== AlchemyAPI

    def alchemy_get_results_to_file(self):
        if self.text_filepath.get() == "(No file selected)":
            self.print_msg_to_stdout_and_gui("No text file selected; aborting...")
            return
        self.alchemy_get_entities_to_file(self.text_filepath.get())
        self.alchemy_get_relations_to_file(self.text_filepath.get())

    def alchemy_list_all_entities(self):
        text_filepath = self.text_filepath.get()
        if text_filepath == "(No file selected)":
            self.print_msg_to_stdout_and_gui("No text file selected; aborting...")
            return
        if not self.alchemy_check_entities_obtained(text_filepath):
            self.print_msg_to_stdout_and_gui("AlchemyAPI entities not yet obtained; aborting...")
            return
        if not self.alchemy_check_relations_obtained(text_filepath):
            self.print_msg_to_stdout_and_gui("AlchemyAPI relations not yet obtained; aborting...")
            return
        
        entities_filepath = self.alchemy_get_entity_result_filepath(text_filepath)
        with open(entities_filepath) as infile:
            response = json.load(infile)

        self.print_msg_to_stdout_and_gui("{} ALL ENTITIES {}".format("=" * 4, "=" * 54))
        entities = alc.get_entities(response)
        for entity in entities:
            text = entity['text']
            ttype = entity['type']
            count = entity['count']
            self.print_msg_to_stdout_and_gui("{} ({}) [count: {}]".format(text, ttype, count))
        self.print_msg_to_stdout_and_gui("-" * 72)
        self.print_msg_to_stdout_and_gui("TOTAL: {}".format(len(entities)))
        self.print_msg_to_stdout_and_gui("=" * 72)

    def alchemy_list_attributed_entities(self):
        text_filepath = self.text_filepath.get()
        if text_filepath == "(No file selected)":
            self.print_msg_to_stdout_and_gui("No text file selected; aborting...")
            return
        if not self.alchemy_check_entities_obtained(text_filepath):
            self.print_msg_to_stdout_and_gui("AlchemyAPI entities not yet obtained; aborting...")
            return
        if not self.alchemy_check_relations_obtained(text_filepath):
            self.print_msg_to_stdout_and_gui("AlchemyAPI relations not yet obtained; aborting...")
            return
            self.print_msg_to_stdout_and_gui("AlchemyAPI relations not yet obtained; aborting...")
            return

        relations_filepath = self.alchemy_get_relation_result_filepath(text_filepath)
        with open(relations_filepath) as infile:
            response = json.load(infile)
        entities = self.alchemy_get_attributed_entities(response)

        self.print_msg_to_stdout_and_gui("{} ATTRIBUTED ENTITIES {}".format("=" * 4, "=" * 47))
        for entity in entities:
            text = entity['text']
            ttype = entity['type']
            self.print_msg_to_stdout_and_gui("{} ({})".format(text, ttype))
        self.print_msg_to_stdout_and_gui("-" * 72)
        self.print_msg_to_stdout_and_gui("TOTAL: {}".format(len(entities)))
        self.print_msg_to_stdout_and_gui("=" * 72)

    #==== OpenCalais

    def calais_get_results_to_file(self):
        if self.text_filepath.get() == "(No file selected)":
            self.print_msg_to_stdout_and_gui("No text file selected; aborting...")
            return
        self.calais_get_response_to_file(self.text_filepath.get())

    def calais_list_all_entities(self):
        text_filepath = self.text_filepath.get()
        if text_filepath == "(No file selected)":
            self.print_msg_to_stdout_and_gui("No text file selected; aborting...")
            return
        if not self.calais_check_results_obtained(text_filepath):
            self.print_msg_to_stdout_and_gui("OpenCalais entities not yet obtained; aborting...")
            return

        response_filepath = self.calais_get_result_filepath(text_filepath)
        with open(response_filepath) as infile:
            response = json.load(infile)

        self.print_msg_to_stdout_and_gui("{} ALL ENTITIES {}".format("=" * 4, "=" * 54))
        entities = cal.get_entities(response)
        for entity in entities:
            name = entity['name']
            ttype = entity['_type']
            self.print_msg_to_stdout_and_gui("{} ({})".format(name, ttype))
        self.print_msg_to_stdout_and_gui("-" * 72)
        self.print_msg_to_stdout_and_gui("TOTAL: {}".format(len(entities)))
        self.print_msg_to_stdout_and_gui("=" * 72)

    def calais_list_attributed_entities(self):
        text_filepath = self.text_filepath.get()
        if text_filepath == "(No file selected)":
            self.print_msg_to_stdout_and_gui("No text file selected; aborting...")
            return
        if not self.calais_check_results_obtained(text_filepath):
            self.print_msg_to_stdout_and_gui("OpenCalais entities not yet obtained; aborting...")
            return

    #==== Combined

    def combined_cross_ref_stanford_alchemy(self):
        if self.text_filepath.get() == "(No file selected)":
            self.print_msg_to_stdout_and_gui("No text file selected")
            return
        self.cross_ref_stanford_alchemy(self.text_filepath.get())

    def combined_compile_attributed_entities(self):
        # TODO: REFACTOR!

        text_filepath = self.text_filepath.get()
        if text_filepath == "(No file selected)":
            self.print_msg_to_stdout_and_gui("No text file selected; aborting...")
            return
        if not self.alchemy_check_entities_obtained(text_filepath):
            self.print_msg_to_stdout_and_gui("AlchemyAPI entities not yet obtained; aborting...")
            return
        if not self.alchemy_check_relations_obtained(text_filepath):
            self.print_msg_to_stdout_and_gui("AlchemyAPI relations not yet obtained; aborting...")
            return
        if not self.calais_check_results_obtained(text_filepath):
            self.print_msg_to_stdout_and_gui("OpenCalais entities not yet obtained; aborting...")
            return

        self.compile_attributed_entities(text_filepath)

    #======== Helper methods

    #==== Stanford NER

    def stanford_count_annotated_files(self):
        annot_dir_files = os.listdir(const.ANNOTATED_DIR)
        return sum([".annot" in filename for filename in annot_dir_files])

    def stanford_generate_prop_config(self, annot_files):
        timestamp = datetime.datetime.today().strftime("%y%m%d_%H%M%S")
        prop_filepath = os.path.join(const.PROP_DIR, "train_{0}.prop".format(timestamp))
        serialize_filepath = os.path.join(const.MODELS_DIR, "model_{0}.ser.gz".format(timestamp))
        if os.name == 'nt':
            serialize_filepath = serialize_filepath.replace("\\", "/")
        with open(prop_filepath, 'w') as outfile:
            outfile.write("trainFileList = {0}\n".format(",".join(annot_files)))
            outfile.write("serializeTo = {0}\n".format(serialize_filepath))
            outfile.write(const.PROP_CONFIG_DEFAULT)
        return prop_filepath, serialize_filepath

    def stanford_create_model(self, prop_filepath):
        if os.name == 'nt':
            args = ["java", "-cp", "stanford-ner.jar", "edu.stanford.nlp.ie.crf.CRFClassifier", "-prop", "{0}".format(prop_filepath)]
        else:
            args = ["java", "-cp", "lib/*:stanford-ner.jar", "edu.stanford.nlp.ie.crf.CRFClassifier", "-prop", "{0}".format(prop_filepath)]
        self.print_msg_to_stdout_and_gui("Executing: {0}".format(" ".join(args)))
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(p.stdout.readline, ""):
            self.print_msg_to_stdout_and_gui(line.strip())
        return p

    def stanford_classify_text(self, model_filepath, text_filepath):
        output_file = os.path.splitext(text_filepath)[0] + ".tagged.txt"
        if os.name == 'nt':
            args = ["java", "-cp", "stanford-ner.jar", "edu.stanford.nlp.ie.crf.CRFClassifier", "-loadClassifier", model_filepath, "-textFile", text_filepath]
        else:
            args = ["java", "-cp", "lib/*:stanford-ner.jar", "edu.stanford.nlp.ie.crf.CRFClassifier", "-loadClassifier", model_filepath, "-textFile", text_filepath]
        self.print_msg_to_stdout_and_gui("Executing: {0}".format(" ".join(args)))
        p = subprocess.Popen(args, stdout=open(output_file, 'w'), stderr=subprocess.PIPE)
        return p, output_file

    def stanford_get_tagged_lines(self, tagged_filepath):
        tagged_tokens = []
        if os.path.exists(tagged_filepath):
            with open(tagged_filepath) as infile:
                lines = infile.read().splitlines()
            for line in lines:
                tagged_tokens.extend([elem.split("/") for elem in line.split(" ")])
        return tagged_tokens

    def stanford_get_tagged_entities(self, tagged_tokens):
        entities = []
        current_entity = ""
        current_token = ""
        current_tag = "O"
        for tagged_token in tagged_tokens:
            if len(tagged_token) != 2:
                continue
            token, tag = tagged_token
            if tag != "O":
                if tag == current_tag:
                    current_entity += " " + token
                    current_tag = tag
                    continue
                else:
                    current_entity = token
                    current_tag = tag
                    continue
            else:
                if current_tag != "O":
                    entities.append((current_entity.strip(), current_tag))
                    current_entity = ""
                    current_tag = tag
                    continue
                else:
                    continue
        return entities

    def stanford_get_tagged_filepath(self, text_filepath):
        return text_filepath.replace(".txt", ".tagged.txt")

    #==== AlchemyAPI

    def alchemy_get_entities_to_file(self, text_filepath):
        result_filepath = self.alchemy_get_entity_result_filepath(text_filepath)
        if os.path.exists(result_filepath):
            self.print_msg_to_stdout_and_gui("AlchemyAPI entity results already obtained for {}; skipping...".format(text_filepath))
            return
        self.print_msg_to_stdout_and_gui("Calling AlchemyAPI...")
        alc.get_entities_to_file(text_filepath, result_filepath)
        self.print_msg_to_stdout_and_gui("AlchemyAPI entity results written to {}".format(result_filepath))
        self.alchemy_update_entities_obtained(text_filepath)

    def alchemy_get_relations_to_file(self, text_filepath):
        result_filepath = self.alchemy_get_relation_result_filepath(text_filepath)
        if os.path.exists(result_filepath):
            self.print_msg_to_stdout_and_gui("AlchemyAPI relation results already obtained for {}; skipping...".format(text_filepath))
            return
        self.print_msg_to_stdout_and_gui("Calling AlchemyAPI...")
        alc.get_relations_to_file(text_filepath, result_filepath)
        self.print_msg_to_stdout_and_gui("AlchemyAPI relation results written to {}".format(result_filepath))
        self.alchemy_update_relations_obtained(text_filepath)

    def alchemy_get_entity_response(self, text_filepath):
        result_filepath = self.alchemy_get_entity_result_filepath(text_filepath)
        if not os.path.exists(result_filepath):
            print("AlchemyAPI entity result file does not exist for {}".format(text_filepath))
        response = json.load(open(result_filepath))
        return response

    def alchemy_get_relation_response(self, text_filepath):
        result_filepath = self.alchemy_get_relation_result_filepath(text_filepath)
        if not os.path.exists(result_filepath):
            print("AlchemyAPI relation result file does not exist for {}".format(text_filepath))
        response = json.load(open(result_filepath))
        return response

    def alchemy_get_entity_result_filepath(self, text_filepath):
        text_file = os.path.split(text_filepath)[1]
        return os.path.join(const.BASE_DIR, const.ALC_DIR, "{}.alc.ent.json".format(text_file))

    def alchemy_get_relation_result_filepath(self, text_filepath):
        text_file = os.path.split(text_filepath)[1]
        return os.path.join(const.BASE_DIR, const.ALC_DIR, "{}.alc.rel.json".format(text_file))

    def alchemy_check_entities_obtained(self, text_filepath):
        result_filepath = self.alchemy_get_entity_result_filepath(text_filepath)
        return os.path.exists(result_filepath)

    def alchemy_check_relations_obtained(self, text_filepath):
        result_filepath = self.alchemy_get_relation_result_filepath(text_filepath)
        return os.path.exists(result_filepath)

    def alchemy_update_entities_obtained(self, text_filepath):
        if self.alchemy_check_entities_obtained(text_filepath):
            self.alchemy_entities_obtained_yesno.set("YES")
            self.alchemy_entities_obtained_display.config(bg="lawn green")
        else:
            self.alchemy_entities_obtained_yesno.set("NO")
            self.alchemy_entities_obtained_display.config(bg="tomato")
        self.update()

    def alchemy_update_relations_obtained(self, text_filepath):
        if self.alchemy_check_relations_obtained(text_filepath):
            self.alchemy_relations_obtained_yesno.set("YES")
            self.alchemy_relations_obtained_display.config(bg="lawn green")
        else:
            self.alchemy_relations_obtained_yesno.set("NO")
            self.alchemy_relations_obtained_display.config(bg="tomato")
        self.update()

    def alchemy_get_attributed_entities(self, response_rel):
        entities = []
        for action_lemm in const.ATTR_VERBS:
            for entity in alc.get_entities_by_action_lemm(response_rel, action_lemm):
                entities.extend(entity)
        return entities

    #==== OpenCalais

    def calais_get_response_to_file(self, text_filepath):
        result_filepath = self.calais_get_result_filepath(text_filepath)
        if os.path.exists(result_filepath):
            self.print_msg_to_stdout_and_gui("OpenCalais results already obtained for {}; skipping...".format(text_filepath))
            return
        self.print_msg_to_stdout_and_gui("Calling OpenCalais...")

        with open(text_filepath) as infile:
            text = infile.read()
        cal.get_calais_to_file(text, result_filepath)
        self.print_msg_to_stdout_and_gui("OpenCalais entity results written to {}".format(result_filepath))
        self.calais_update_results_obtained(text_filepath)

    def calais_get_result_filepath(self, text_filepath):
        text_file = os.path.split(text_filepath)[1]
        return os.path.join(const.BASE_DIR, const.CAL_DIR, "{}.cal.json".format(text_file))

    def calais_update_results_obtained(self, text_filepath):
        if self.calais_check_results_obtained(text_filepath):
            self.calais_results_obtained_yesno.set("YES")
            self.calais_results_obtained_display.config(bg="lawn green")
        else:
            self.calais_results_obtained_yesno.set("NO")
            self.calais_results_obtained_display.config(bg="tomato")
        self.update()

    def calais_check_results_obtained(self, text_filepath):
        result_filepath = self.calais_get_result_filepath(text_filepath)
        return os.path.exists(result_filepath)

    # TODO
    def calais_get_attributed_entities(self, response):
        return

    #==== AlchemyAPI + OpenCalais

    # TODO
    def cross_ref_alchemy_calais(self, entities_alc, entities_cal):
        return

    #==== AlchemyAPI + Stanford NER

    def cross_ref_stanford_alchemy(self, text_filepath):
        #tagged_filepath = self.tagged_filepath.get()
        #if tagged_filepath == "(No file selected)":
        #    self.print_msg_to_stdout_and_gui("Tagged file not selected")
        #    return
        tagged_filepath = self.stanford_get_tagged_filepath(text_filepath)
        if not os.path.exists(tagged_filepath):
            self.print_msg_to_stdout_and_gui("Tagged file [{}] does not exist".format(tagged_filepath))
            return

        relations_filepath = self.alchemy_get_relation_result_filepath(text_filepath)
        if not os.path.exists(relations_filepath):
            self.print_msg_to_stdout_and_gui("Alchemy relation results file [{}] does not exist".format(relations_filepath))
            return

        with open(relations_filepath) as infile:
            response = json.load(infile)
        entities_alchemy = self.alchemy_get_attributed_entities(response)

        tagged_tokens = self.stanford_get_tagged_lines(tagged_filepath)
        entities_stanford = self.stanford_get_tagged_entities(tagged_tokens)

        self.print_msg_to_stdout_and_gui("{} {}".format(len(entities_alchemy), len(entities_stanford)))
        for entity_alchemy in entities_alchemy:
            text = entity_alchemy['text']
            for entity_stanford in entities_stanford:
                self.print_msg_to_stdout_and_gui("{} , {}".format(text, entity_stanford[0]))
                if self.entity_names_match(text, entity_stanford[0]):
                    self.print_msg_to_stdout_and_gui("*** MATCH! ***")

    #==== Combined

    def compile_attributed_entities(self, text_filepath):
        tagged_filepath = self.stanford_get_tagged_filepath(text_filepath)
        if not os.path.exists(tagged_filepath):
            self.print_msg_to_stdout_and_gui("Tagged file [{}] does not exist".format(tagged_filepath))
            return
        # TODO: REFACTOR!

        attr_entities_alc_proc = []
        relations_filepath = self.alchemy_get_relation_result_filepath(text_filepath)
        with open(relations_filepath) as infile:
            response = json.load(infile)
        attr_entities_alc = self.alchemy_get_attributed_entities(response)

        for entity in attr_entities_alc:
            attr_entities_alc_proc.append({'name': entity['text'], 'cat': entity['type']})

        #entities_cal_proc = []
        #response_filepath = self.calais_get_result_filepath(text_filepath)
        #with open(response_filepath) as infile:
        #    response = json.load(infile)
        #entities_cal = self.calais_get_attributed_entities(response)

        #for entity in entities_cal:
        #    entities_cal_proc.append({'name': entity['name'], 'cat': entity['_type']})

        entities_stn_proc = []

        tagged_tokens = self.stanford_get_tagged_lines(tagged_filepath)
        entities_stn = self.stanford_get_tagged_entities(tagged_tokens)
        print(entities_stn)

        for entity in entities_stn:
            entities_stn_proc.append({'name': entity[0], 'cat': entity[1]})

        entities_compiled = []

        for entity_alc in attr_entities_alc_proc:
            entity_compiled = {'name': entity_alc['name'], 'cat_alc': entity_alc['cat'],
                               'cat_cal': [], 'cat_stn': []}

            #for entity_cal in entities_cal_proc:
            #    if entity_alc['name'] == entity_cal_proc['name']:
            #        entity_compiled['cat_cal'].append(entity_cal_proc['cat'])

            for entity_stn in entities_stn_proc:
                print(entity_alc['name'], entity_stn['name'])
                if self.entity_names_match(entity_alc['name'], entity_stn['name']):
                    entity_compiled['cat_stn'].append(entity_stn['cat'])

            entities_compiled.append(entity_compiled)

        for entity in entities_compiled:
            line = "{} {} {} {}".format(entity['name'], entity['cat_alc'], entity['cat_cal'], entity['cat_stn'])
            self.print_msg_to_stdout_and_gui(line)

    #==== Misc

    def entity_names_match(self, entity_name_1, entity_name_2):
        return entity_name_1.strip().lower() == entity_name_2.strip().lower()

    def print_msg_to_stdout_and_gui(self, msg, write_to_log=False):
        print(msg)

        if write_to_log: parent.write_to_log(msg + "\n")

        self.output_text.insert(tk.END, msg + "\n")
        self.output_text.see(tk.END)
        self.update()
