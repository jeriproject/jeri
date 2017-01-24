"""Miscellaneous utility functions."""

import os

def is_html(filepath):
    return has_ext(filepath, "html")

def is_txt(filepath):
    return has_ext(filepath, "txt")

def is_json(filepath):
    return has_ext(filepath, "json")

def has_ext(filepath, ext):
    if ext[0] != ".":
        ext = "." + ext
    return os.path.splitext(filepath)[1] == ext
