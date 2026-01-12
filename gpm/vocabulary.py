import os

# META #########################################################################

PATH = os.path.dirname(os.path.abspath(__file__))

# ALPHABET #####################################################################

BANNED = ''.join(chr(__i) for __i in (0x20, 0x22, 0x27, 0x28, 0x29, 0x5b, 0x5c, 0x5d, 0x60, 0x7b, 0x7c, 0x7d))  #  "\'()[\\]`{|}
SPACES = ' '                                                                                                    #
DIGITS = '0123456789'                                                                                           # 0-9
UPPERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'                                                                           # A-Z
LOWERS = UPPERS.lower()                                                                                         # a-z
SYMBOLS = ''.join(set(chr(__i) for __i in range(0x20, 0x7f)) - set(BANNED + DIGITS + UPPERS + LOWERS))          # =,%~?>-.*^@&_+</!$#;:

# VOCABULARY ###################################################################

WORDS = open(os.path.join(PATH, 'data.txt'), 'r').read().split('\n')

# FILTER #######################################################################

def check(text: str, allowed: list) -> bool:
    return all(__c in allowed for __c in text)

# COMPOSITION ##################################################################

def alphabet(lowers: bool=True, uppers: bool=True, digits: bool=True, symbols: bool=False, spaces: bool=False) -> str:
    return sorted(set(lowers * LOWERS + uppers * UPPERS + digits * DIGITS + symbols * SYMBOLS + spaces * SPACES))

def compose(lowers: bool=True, uppers: bool=True, digits: bool=True, symbols: bool=False, spaces: bool=False, words: bool=False) -> str:
    __alpha = alphabet(lowers=lowers, uppers=uppers, digits=digits, symbols=symbols, spaces=spaces)
    # either all lower or all upper, no mixed case
    __words = set([__w.lower() for __w in WORDS] + [__w.upper() for __w in WORDS])
    # keep only the words made from the alphabet
    __words = list(filter(lambda __w: check(text=__w, allowed=__alpha), __words))
    # choose between character and word levels
    return __words if words else __alpha

# MAPPINGS ####################################################################

def mappings(vocabulary: list) -> dict:
    __dim = len(vocabulary)
    # actual mappings
    __itos = {__i: __c for __i, __c in enumerate(vocabulary)}
    __stoi = {__c: __i for __i, __c in enumerate(vocabulary)}
    # blank placeholder
    __blank_c = __itos[0] # chr(0)
    __blank_i = 0
    # s => i
    def __encode(_c: str) -> int:
        return __stoi.get(_c, __blank_i)
    # i => s
    def __decode(_i: int) -> str:
        return __itos.get(_i % __dim, __blank_c)
    # return both
    return {'encode': __encode, 'decode': __decode}

# ENCODING ####################################################################

def encode(text: str, stoi: callable) -> list:
    return [stoi(__c) for __c in text] # defaults to 0 if a character is not in the vocabulary

def decode(sequence: list, itos: callable, separator: str='') -> list:
    return separator.join([itos(__i) for __i in sequence]) # defaults to the first character
