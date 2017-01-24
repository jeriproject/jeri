"""
An early attempt at creating a graphical interface for the annotator.

May be too difficult and not useful enough to justify the effort...
"""

import copy
import datetime
import glob
import json
import os
import sys
import Tkinter as tk

import jeri.pipeline.alchemy_tools as alc
import jeri.pipeline.calais_tools as cal
import jeri.pipeline.gensim_tools as gsm
import jeri.pipeline.nltk_tools as nlt

reload(sys)
sys.setdefaultencoding('utf-8')

BASE_DIR = "tstar_search_carding_160507"
TXT_DIR = os.path.join(BASE_DIR, "parsed")
ALC_DIR = os.path.join(BASE_DIR, "alc")
ALC_ENT_DIR = os.path.join(ALC_DIR, "ent")
ALC_REL_DIR = os.path.join(ALC_DIR, "rel")
CAL_DIR = os.path.join(BASE_DIR, "cal")
TOK_DIR = os.path.join(BASE_DIR, "tok")
ANNOT_DIR = "annotated"
MEMORY_FILEPATH = os.path.join(ANNOT_DIR, "memory.json")
FILES_INCOMPLETE_FILEPATH = os.path.join(ANNOT_DIR, "files_incomplete.json")

CAT_STRS = (
    "1. Organizations and Businesses",
    "2. Authority",
    "3. Experts",
    "4. Celebrities",
    "5. Media",
    "6. Unaffiliated",
    "7. (Skip)"
)
CAT_LABELS = ("ORG", "AUT", "EXP", "CEL", "MED", "UNA")

ALC_ENT_TYPES_TO_OMIT = ("City", "Quantity")
CAL_ENT_TYPES_TO_OMIT = ("City")

MIN_SIMILARITY_SCORE = 0.1

class JeriAnnotator(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        parent.write_to_log("==== START ANNOTATOR: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        self.rowconfigure(0, weight=1)
        self.output_text = self.make_text_frame()

        self.yes = False
        self.no = False
        self.quit = False

        if not os.path.exists(MEMORY_FILEPATH):
            save_to_memory({})
        if not os.path.exists(FILES_INCOMPLETE_FILEPATH):
            save_files_incomplete({})

        self.names_processed = load_from_memory()
        self.files_incomplete = load_files_incomplete()

        self.txt_paths = sorted(get_txt_files(TXT_DIR))
        self.txt_path_i = 0
        self.det_i = 0

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

    def resume_current_txt(self):
        txt_path = self.txt_paths[self.txt_path_i]
        txt_file = os.path.split(txt_path)[1]
        annot_path = os.path.join(ANNOT_DIR, "{0}.annot".format(txt_file))
        start = None

    def start_next_txt(self):
        return



    #    for txt_path in txt_paths:
    #        txt_file = os.path.split(txt_path)[1]
    #        annot_path = os.path.join(ANNOT_DIR, "{0}.annot".format(txt_file))
    #        start = None

    #        print("=" * 79)
    #        print("")

    #        if len(glob.glob(annot_path + "*")) == 0:
    #            if txt_file not in files_incomplete.keys():
    #                prompt = "Start annotating \"{0}\"? [y/n/q] ".format(txt_file)
    #            else:
    #                prompt = "Continue annotating \"{0}\"? [y/n/q] ".format(txt_file)
    #        else:
    #            prompt = "\"{0}\" has already been annotated; start new annotation? [y/n/q] ".format(txt_file)


    ##        while not (start == "y" or start == "n" or start == "q"):
    #            #start = raw_input(prompt)
    #            #start = input(prompt)
    #            if start == "y":
    #                break
    #            if start == 'q':
    #                save_to_memory(names_processed)
    #                sys.exit()
            
    #        if start == "n":
    #            continue                

    #        paths = get_all_filepaths(txt_path)
    #        alc_ent_path = paths['alc_ent']
    #        alc_rel_path = paths['alc_rel']
    #        cal_path = paths['cal']
    #        tok_path = paths['tok']

    #        text = get_text_from_txt(txt_path)
    #        dets = []
    #        dets.extend(get_cal_detections_from_json(cal_path, CAL_ENT_TYPES_TO_OMIT))
    #        #dets.extend(get_alc_detections_from_json(alc_ent_path, ALC_ENT_TYPES_TO_OMIT))
    #        # Sort by name
    #        dets = sorted(dets, key=lambda k: k['name'])
    #        toks = get_toks_from_tok(tok_path)
    #        toks_annot = copy.deepcopy(toks)
    #        #toks_annot = toks.copy()

    #        n_dets = len(dets)
    #        for i, detect in enumerate(dets):
    #            if txt_file in files_incomplete.keys() and i < files_incomplete[txt_file]:
    #                print("Already annotated, skipping...")
    #                continue

    #            name = detect['name']
    #            exact = detect['exact']
    #            det = detect['detection']

    #            if name in names_processed.keys():
    #                # Entity has already been labelled
    #                label = names_processed[name]
    #                if label == 'SKIP':
    #                    continue

    #            else:
    #                print("")
    #                print("-" * 79)
    #                print("[{0}/{1}]".format(i + 1, n_dets))
    #                print("")
    #                print("Name   : {0}".format(name))
    #                print("Exact  : {0}".format(exact))
    #                print("Context: \"{0}\"".format(det))
    #                print("")


    #                for cat_str in CAT_STRS:
    #                    print(cat_str)

    #                print("")

    #                suggestion_found = False

    #                if load_from_memory() != {}:
    #                    docs = gsm.get_documents_from_memory(MEMORY_FILEPATH)
    #                    dictionary, corpus = gsm.get_dictionary_corpus_from_documents(docs)
    #                    sims = gsm.get_similarity_scores_from_dictionary_corpus(dictionary, corpus, name)
    #                    guess_cat, guess_score = gsm.get_best_guess_and_score(CAT_LABELS, sims)

    #                    if guess_score < MIN_SIMILARITY_SCORE:
    #                        print("Suggested: None")
    #                    else:
    #                        print("Suggested: {0} ({1:.2f} %) [Leave blank to use]".format(guess_cat, guess_score * 100))
    #                        suggestion_found = True

    #                else:
    #                    print("[At least one annotated article required for category suggestion]")

    #                print("")

    #                select = None
    #                while not (select == "1" or select == "2" or select == "3" or
    #                           select == "4" or select == "5" or select == "6" or
    #                           select == "7" or select == "q"):
    #                    select = raw_input("Select [1/2/3/4/5/6/7/q/(blank)]: ")
    #                    #select = input("Select [1/2/3/4/5/6/7/q]: ")
    #                    if select == "":
    #                        if suggestion_found:
    #                            break
    #                        else:
    #                            print("")
    #                            print("No suggestion found, please select a category.")
    #                            print("")

    #                if select == "q":
    #                    files_incomplete[txt_file] = i
    #                    save_files_incomplete(files_incomplete)
    #                    save_to_memory(names_processed)
    #                    sys.exit()

    #                if select == "7":
    #                    names_processed[name] = 'SKIP'
    #                    continue

    #                if select == "" and suggestion_found:
    #                    label = guess_cat
    #                else:
    #                    cat = int(select) - 1
    #                    label = CAT_LABELS[cat]

    #                names_processed[name] = label

    #            exact_toks = nlt.get_tokens(exact)
    #            det_toks = nlt.get_tokens(det)

    #            det_match_indices = get_sublist_match_indices(det_toks, toks)
    #            if det_match_indices is None:
    #                continue
    #            det_match = toks[det_match_indices[0] : det_match_indices[1]]

    #            exact_match_indices = get_sublist_match_indices(exact_toks, det_toks)
    #            if exact_match_indices is None:
    #                continue

    #            for i in range(det_match_indices[0] + exact_match_indices[0],
    #                           det_match_indices[0] + exact_match_indices[1]):
    #                toks_annot[i] += "\t" + label
    #                print("ANNOTATED: " + toks_annot[i])

    #        with open(annot_path + datetime.datetime.today().strftime("_%y%m%d_%H%M%S"), 'w') as annot_out:
    #            for tok in toks_annot:
    #                elems = tok.split("\t")
    #                if len(elems) == 1:
    #                    tok = "{0}\tO".format(elems[0])
    #                elif len(elems) >= 2:
    #                    # TODO: how to resolve conflicts? (multiple different labels)
    #                    tok = "{0}\t{1}".format(elems[0], elems[1])
    #                annot_out.write("{0}\n".format(tok))

    #        print("")
    #        print("Finished annotating \"{0}\"!".format(txt_file))
    #        print("")

    #        save_to_memory(names_processed)

    #    save_to_memory(names_processed)

    def print_msg_to_stdout_and_gui(self, msg, write_to_log=False):
        print(msg)

        if write_to_log: parent.write_to_log(msg + "\n")

        self.output_text.insert(tk.END, msg + "\n")
        self.output_text.see(tk.END)
        self.update()


def get_txt_files(txt_dir):
    return glob.glob(os.path.join(txt_dir, "*.txt"))

def get_text_from_txt(txt_file):
    with open(txt_file, 'r') as infile:
        text = infile.read()
    return text

def get_toks_from_tok(tok_file):
    with open(tok_file, 'r') as infile:
        toks = infile.read().splitlines()
    return [tok.strip() for tok in toks]

def get_alc_detections_from_json(alc_file, types_to_omit=[]):
    detections = []
    with open(alc_file, 'r') as infile:
        resp = json.load(infile)
        entities = alc.get_entities(resp)
        entities = filter(lambda e: e['type'] not in types_to_omit, entities)
        for e in entities:
            detections.append({'name': e['text'], 'detection': e['text'], 'exact': e['text']})
    return detections

def get_cal_detections_from_json(cal_file, types_to_omit=[]):
    detections = []
    with open(cal_file, 'r') as infile:
        resp = json.load(infile)
        entities = cal.get_entities(resp)
        entities = filter(lambda e: '_type' in e.keys() and e['_type'] not in types_to_omit, entities)
        for e in entities:
            for i in e['instances']:
                detections.append({'name': e['name'], 'detection': i['detection'].replace("[", "").replace("]", ""), 'exact': i['exact']})
    return detections

def get_detection_text_indices(text, detection):
    det = (detection['detection']).replace('[', '').replace(']', '')
    exact = detection['exact']
    det_start_idx = text.find(det)
    det_end_idx = det_start_idx + len(det)
    exact_start_idx = det.find(exact)
    exact_end_idx = exact_start_idx + len(exact)
    return det, (det_start_idx, det_end_idx), exact, (exact_start_idx, exact_end_idx)

def get_all_filepaths(txt_path):
    txt_file = os.path.split(txt_path)[1]
    alc_ent_path = os.path.join(ALC_ENT_DIR, txt_file + ".alc.ent.json")
    alc_rel_path = os.path.join(ALC_REL_DIR, txt_file + ".alc.rel.json")
    cal_path = os.path.join(CAL_DIR, txt_file + ".cal.json")
    tok_path = os.path.join(TOK_DIR, txt_file + ".tok")

    return {'txt': txt_path, 'alc_ent': alc_ent_path, 'alc_rel': alc_rel_path,
            'cal': cal_path, 'tok': tok_path}

def get_sublist_match_indices(sublist, llist):
    match_indices = None
    for i, _ in enumerate(llist):
        if llist[i : i + len(sublist)] == sublist:
            match_indices = (i, i + len(sublist))
    return match_indices

def load_from_json(filepath):
    with open(filepath) as infile:
        return json.load(infile)

def load_from_memory():
    return load_from_json(MEMORY_FILEPATH)

def load_files_incomplete():
    return load_from_json(FILES_INCOMPLETE_FILEPATH)

def save_to_json(filepath, data):
    with open(filepath, 'w') as outfile:
        json.dump(data, outfile)

def save_to_memory(names_processed):
    save_to_json(MEMORY_FILEPATH, names_processed)

def save_files_incomplete(files_incomplete):
    save_to_json(FILES_INCOMPLETE_FILEPATH, files_incomplete)
