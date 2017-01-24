import os

BASE_DIR = os.getcwd()

ANNOTATED_DIR = "annotated"
ANNOT_GLOB_PATTERN = "*.annot*"
MODEL_EXTENSION = ".ser.gz"
TEXT_EXTENSION = ".txt"
TAGGED_EXTENSION = ".tagged.txt"

PROP_CONFIG_DEFAULT = """
map = word=0,answer=1
useClassFeature=true
useWord=true
useNGrams=true
noMidNGrams=true
useDisjunctive=true
maxNGramLeng=6
usePrev=true
useNext=true
useSequences=true
usePrevSequences=true
maxLeft=1
useTypeSeqs=true
useTypeSeqs2=true
useTypeySequences=true
wordShape=chris2useLC
"""

PROP_DIR = "prop"
MODELS_DIR = "models"

ALC_DIR = "alchemy_results"
CAL_DIR = "opencalais_results"

ATTR_VERBS = ("say", "write", "claim", "defend", "read")

ARTICLE_DIR = "tstar_search_carding_160507"
ARTICLE_TXT_DIR = os.path.join(ARTICLE_DIR, "parsed")
ARTICLE_ALC_DIR = os.path.join(ARTICLE_DIR, "alc")
ARTICLE_ALC_ENT_DIR = os.path.join(ARTICLE_ALC_DIR, "ent")
ARTICLE_ALC_REL_DIR = os.path.join(ARTICLE_ALC_DIR, "rel")
ARTICLE_CAL_DIR = os.path.join(ARTICLE_DIR, "cal")
ARTICLE_TOK_DIR = os.path.join(ARTICLE_DIR, "tok")
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