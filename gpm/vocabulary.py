# VOCABULARY SECTIONS ##########################################################

BANNED = ''.join(chr(__i) for __i in (0x20, 0x22, 0x27, 0x28, 0x29, 0x5b, 0x5c, 0x5d, 0x60, 0x7b, 0x7c, 0x7d))  #  "\'()[\\]`{|}
DIGITS = '0123456789'                                                                                           # 0-9
UPPERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'                                                                           # A-Z
LOWERS = UPPERS.lower()                                                                                         # a-z
SYMBOLS = ''.join(set(chr(__i) for __i in range(0x20, 0x7f)) - set(BANNED + DIGITS + UPPERS + LOWERS))          # =,%~?>-.*^@&_+</!$#;:

# VOCABULARY ###################################################################

def compose(lower: bool=True, upper: bool=True, digits: bool=True, symbols: bool=False) -> str:
    return sorted(set(lower * LOWERS + upper * UPPERS + digits * DIGITS + symbols * SYMBOLS))

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

def decode(sequence: list, itos: callable) -> list:
    return ''.join([itos(__i) for __i in sequence]) # defaults to the first character
