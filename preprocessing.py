"""
Preprocessing utilities for text/sentence embedding.

Note that the following functions are not computationally optimized yet.
"""


from re import sub as re_sub

# from spacy import load as spacy_load

from emoji import demojize


IRRELEVANT_PART_OF_SPEECH_TAGS = [
    # universal part-of-speech tags defined as irrelevant:
    # (reference: https://universaldependencies.org/docs/u/pos/)
    'ADP',  # adposition
    'AUX',  # auxiliary verb
    'CONJ',  # coordinating conjunction
    "EOL",  # end of line
    'PUNCT',  # punctuation
    'SCONJ',  # subordinating conjunction
    'SPACE',  # space
    # English-specific part-of-speech tags defined as irrelevant:
    # (references: https://www.ling.upenn.edu/courses/Fall_2003/ling001/
    # penn_treebank_pos.html,
    # https://github.com/explosion/spaCy/blob/master/spacy/glossary.py#L43)
    ".",  # punctuation mark, sentence closer
    ",",  # punctuation mark, comma
    "-LRB-",  # left round bracket
    "-RRB-",  # right round bracket
    "``",  # opening quotation mark
    '""',  # closing quotation mark
    "''",  # closing quotation mark
    ":",  # punctuation mark, colon or ellipsis
    "CC",  # conjunction, coordinating
    "HYPH",  # punctuation mark, hyphen
    "IN",  # conjunction, subordinating or preposition
    "LS",  # list item marker
    "POS",  # possessive ending
    "TO",  # infinitival "to"
    "SP",  # space (English), sentence-final particle (Chinese)
    "NFP",  # superfluous punctuation
    "BES",  # auxiliary "be"
]

def preprocess(sentence_text: str) -> str:
    """
    Preprocess in and end-to-end fashion the input text for later accurate
    sentence embedding computation by replacing emojis with the respective
    words in their official names.
    """
    return re_sub(
        ' +',
        ' ',
        replace_emojis_with_words(sentence_text)
    )

def replace_emojis_with_words(sentence_text: str) -> str:
    """
    Replace emojis with the respective words in their official names.
    """
    return demojize(sentence_text, delimiters=(" ", " "), ).replace("_", " ")
