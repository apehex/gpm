import itertools
import re

import tensorflow as tf

import gpm.model
import gpm.vocabulary

# DEFAULT VOCABULARIES #########################################################

INPUT_VOCABULARY = ''.join(chr(__i) for __i in range(128)) # all ASCII characters
OUTPUT_VOCABULARY = INPUT_VOCABULARY # placeholder

# DEFAULT META #################################################################

N_INPUT_DIM = len(INPUT_VOCABULARY) # all ASCII characters
N_OUTPUT_DIM = N_INPUT_DIM # placeholder, it depends on the user settings

N_CONTEXT_DIM = 8
N_EMBEDDING_DIM = 128

N_PASSWORD_DIM = 16
N_PASSWORD_NONCE = 1

# PREPROCESS ##################################################################

def remove_prefix(text: str) -> str: # "github.com" and "https://github.com"
    __r = r'^((?:ftp|https?):\/\/)'
    return re.sub(pattern=__r, repl='', string=text, flags=re.IGNORECASE)

def remove_suffix(text: str) -> str:
    __r = r'(\/+)$'
    return re.sub(pattern=__r, repl='', string=text, flags=re.IGNORECASE)

def remove_spaces(text: str) -> str:
    return text.replace(' ', '').replace('\t', '')

def reduce_ascii(text: str) -> str:
    return ''.join(chr(ord(__c) % 128) for __c in text)

def preprocess(target: str, login: str) -> list:
    __left = remove_suffix(remove_prefix(remove_spaces(reduce_ascii(target.lower()))))
    __right = remove_spaces(reduce_ascii(login.lower()))
    return __left + '|' + __right

# ENTROPY #####################################################################

def accumulate(x: int, y: int, n: int) -> int:
    return (x + y) % n

def feed(source: list, nonce: int, dimension: int) -> iter:
    __func = lambda __x, __y: accumulate(x=__x, y=__y + nonce, n=dimension) # add entropy by accumulating the encodings
    return itertools.accumulate(iterable=itertools.cycle(source), func=__func) # infinite iterable

# INPUTS ######################################################################

def tensor(feed: 'Iterable[int]', length: int, context: int) -> tf.Tensor:
    __x = [[next(feed) for _ in range(context)] for _ in range(length)]
    return tf.constant(tf.convert_to_tensor(value=__x, dtype=tf.dtypes.int32))

# OUTPUTS #####################################################################

def password(model: tf.keras.Model, data: tf.Tensor, itos: callable, separator: str='') -> str:
    __y = tf.squeeze(model(data, training=False))
    __p = list(tf.argmax(__y, axis=-1).numpy())
    return gpm.vocabulary.decode(__p, itos=itos, separator=separator)

# PROCESS #####################################################################

def process(
    master_key: str,
    login_target: str,
    login_id: str,
    password_length: int,
    password_nonce: int,
    include_lowers: bool,
    include_uppers: bool,
    include_digits: bool,
    include_symbols: bool,
    include_spaces: bool,
    include_words: bool,
    input_vocabulary: str=INPUT_VOCABULARY,
    model_context_dim: int=N_CONTEXT_DIM,
    model_embedding_dim: int=N_EMBEDDING_DIM
) -> str:
    # separate the words by spaces
    __separator = int(include_spaces and include_words) * ' '
    # input vocabulary
    __input_mappings = gpm.vocabulary.mappings(vocabulary=input_vocabulary)
    __input_dim = len(input_vocabulary)
    # output vocabulary
    __output_vocabulary = gpm.vocabulary.compose(lowers=include_lowers, uppers=include_uppers, digits=include_digits, symbols=include_symbols, spaces=include_spaces, words=include_words)
    __output_mappings = gpm.vocabulary.mappings(vocabulary=__output_vocabulary)
    __output_dim = len(__output_vocabulary)
    # inputs
    __inputs = preprocess(target=login_target, login=login_id)
    __source = gpm.vocabulary.encode(text=__inputs, stoi=__input_mappings['encode'])
    __feed = feed(source=__source, nonce=password_nonce, dimension=__input_dim)
    __data = tensor(feed=__feed, length=password_length, context=model_context_dim)
    # model
    __model = gpm.model.create(key_str=master_key, n_input_dim=__input_dim, n_output_dim=__output_dim, n_context_dim=model_context_dim, n_embedding_dim=model_embedding_dim)
    # password
    return password(model=__model, data=__data, itos=__output_mappings['decode'], separator=__separator)
