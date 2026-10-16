"""Names for the numeric GFF4 field IDs we care about.

GFF4 stores field labels as numbers. These IDs come from community reverse
engineering of Dragon Age: Origins (the DA toolset wiki and xoreos). Unknown
IDs are kept as plain numbers in dumps, so nothing is lost.
"""

# Data tables (.gda, GFF type "G2DA")
G2DA_COLUMN_NAME = 10000
G2DA_COLUMN_HASH = 10001
G2DA_COLUMN_LIST = 10002
G2DA_ROW_LIST = 10003
G2DA_ROW_DATA = 10004
G2DA_COLUMN_1 = 10005  # column n is G2DA_COLUMN_1 + n - 1
G2DA_COLUMN_TYPE = 10999

# Conversations (.cnv, GFF type "CNV ")
CONV_STARTING_LIST = 12000
CONV_STARTING_INDEX = 12001
CONV_LINE_LIST = 12002
CONV_END = 12003
CONV_VO_BANK = 12004
CONV_STAGE_NAME = 12100
CONV_STAGE_MAP = 12101
CONV_KEY_TAG = 12102
CONV_VALUE_TAG = 12103
CONV_STAGE_AT_CURRENT_LOCATION = 12104
CONV_LINE_TEXT = 12201
CONV_LINE_SPEAKER = 12202
CONV_LINE_LISTENER = 12203
CONV_LINE_GAME_LANGUAGE = 12204
CONV_LINE_ICON = 12205
CONV_LINE_VISIBILITY = 12206
CONV_LINE_AMBIENT = 12207
CONV_LINE_COND = 12208
CONV_LINE_ACTION = 12209
CONV_LINE_CUT_RESREF = 12210
CONV_LINE_CUT = 12211
CONV_LINE_CUT_MAP = 12212
CONV_LINE_ANIMATION = 12213
CONV_LINE_SKIP = 12214
CONV_LINE_FAST_PATH = 12215
CONV_LINE_NO_VO_INGAME = 12216
CONV_LINE_REVERT_ANIM = 12217
CONV_LINE_SLIDESHOW_TEXTURE = 12218
CONV_PLOT_GUID = 12300
CONV_PLOT_FLAG = 12301
CONV_PLOT_TEST = 12302
CONV_SCRIPT = 12303
CONV_SCRIPT_PARAMETER = 12304
CONV_LINE_CHILDREN_LIST = 12400
CONV_LINE_ACTIVE = 12500

# Plots (.plo)
PLOT_FLAGS = 13000
PLOT_FLAG_ID = 13001
PLOT_FLAG_NAME = 13002
PLOT_FLAG_REWARD = 13003
PLOT_FLAG_JOURNAL = 13004
PLOT_FLAG_ENDS_PLOT = 13005
PLOT_FLAG_MULTI_REWARD = 13006
# Observed on the retail plots: the plot's GUID, its script, and the list of
# PLOT structs at the root of a "PLTS" file.
PLOT_GUID = 13007
PLOT_SCRIPT = 13009
PLOT_LIST = 13016

# Cutscenes (.cut, GFF type "CUT "). Observed on the Human Noble cutscenes: a
# list of actors (the MASTER track, characters, cameras, sounds), each with a
# generic list of tracks (TRAK, AANI animation, ASLN spoken line, ACSP sound...).
CUT_AREA = 3010
CUT_LENGTH = 5000
CUT_END_SCRIPT = 5001
CUT_ACTOR_LIST = 5200
CUT_TRACK_LIST = 5206
CUT_ACTOR_TAG = 5216
CUT_TRACK_START = 5301
CUT_TRACK_END = 5302
CUT_LINE_CONVERSATION = 5562  # ASLN: the conversation the line comes from
CUT_SOUND_EVENT = 5670  # ACSP: the FMOD event it plays

# Talk tables (.tlk, GFF type "TLK ")
TALK_BUCKET_LIST = 19000
TALK_STRING_LIST = 19001
TALK_STRING_ID = 19002
TALK_STRING = 19003
HUFF_TALK_STRING_ID = 19004
HUFF_TALK_STRING_BIT_OFFSET = 19005
HUFF_TALK_STRING_LIST = 19006
HUFF_TALK_STRING_HUFF_TREE = 19007
HUFF_TALK_STRING_BIT_STREAM = 19008


def _build_names() -> dict[int, str]:
    names = {value: key.lower() for key, value in globals().items()
             if key.isupper() and isinstance(value, int)}
    for n in range(2, 300):
        names[G2DA_COLUMN_1 + n - 1] = f"g2da_column_{n}"
    return names


NAMES: dict[int, str] = _build_names()
