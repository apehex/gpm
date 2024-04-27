"""Tensorflow port of the tutorial by Andrej Karpathy: https://github.com/karpathy/nn-zero-to-hero/blob/master/lectures/makemore/"""

import datetime
import functools
import os

import tensorflow as tf
import tensorflow_datasets as tfds

import mlable.models.tokun.layers as _mmtl
import mlable.models.tokun.pipeline as _mmtp
import mlable.tensorflow.io as _mti
import mlable.tensorflow.layers as _mtl
import mlable.tensorflow.optimizers as _mto
import mlable.tensorflow.sampling as _sam
import mlable.tensorflow.summary as _sum

# META ########################################################################

N_DEPTH = 3 # D
N_TOKEN_DIM = 4 # G
N_ENCODING_DIM = 256 # U
N_EMBEDDING_DIM = N_ENCODING_DIM # E
N_LATENT_DIM = N_EMBEDDING_DIM # L

N_EPOCHS = 32
N_EPOCHS_RAMPUP = 16
N_EPOCHS_SUSTAIN = 0

N_BATCH = 128 # number of samples per batch
N_SAMPLE = 128 # number of characters per sample (=> N_TOKEN_DIM * N_SAMPLE integers per sample)

R_MIN = 0.0001
R_MAX = 0.001
R_EXP = .8

VERSION = 'tokun-1-keras-660k'

# DATA ########################################################################

# DATA_TRAIN, DATA_TEST = tfds.load('mlqadd', split=['train', 'test'], as_supervised=True, shuffle_files=True, data_dir='~/.cache/tensorflow/', builder_kwargs={'train_lang': ['en'], 'test_lang': ['es']})
LANG = ['ar', 'de', 'en', 'es', 'hi', 'vi', 'zh']
DATA = {__l: tfds.load('mlqa/' + __l, split='test', as_supervised=False, shuffle_files=True, data_dir='~/.cache/tensorflow/', batch_size=N_BATCH) for __l in LANG}

# Single sample for manual testing
TEST = """Reinforcement learning from human feedback (RLHF) (deutsch Bestärkendes Lernen durch menschliche Rückkopplung) steht für maschinelles Lernen, bei dem ein Software-Agent selbständig eine Strategie (Policy) erlernt, um erhaltene Belohnungen zu maximieren. Dabei wird dem Agenten nicht vorgezeigt, welche Aktion in welcher Situation die beste ist, sondern er erhält durch eine Bewertungseinheit zu bestimmten Zeitpunkten durch Rückkopplung (Feedback) aus der Umwelt eine reellwertige Belohnung, die auch negativ sein kann. Im Gegensatz zum klassischen bestärkenden Lernen bestimmt zusätzlich eine Bewertungseinheit eine weitere Belohnung nach Überprüfen von Resultaten des Software-Agents durch Personen, welche das sogenannte Alignment[1] mit menschlicher Denkweise, Erwartung und Wertvorstellung beurteilen.[2][3][4] Das Unternehmen Open AI hat diese zusätzliche, nachträgliche Feineinstellung mittels RLHF bei der Weiterentwicklung von ChatGPT Version 3.5 auf Version 4.0 eingeführt.[5]"""

# MODEL #######################################################################

class Encoder(tf.keras.models.Model):
    def __init__(self, depth: int, token_dim: int, encoding_dim: int, embedding_dim: int, latent_dim: int, batch_dim: int=None, attention: bool=False, **kwargs) -> None:
        super(Encoder, self).__init__(**kwargs)
        self._encoder = tf.keras.Sequential([
            tf.keras.Input(shape=(encoding_dim,), batch_size=batch_dim, name='input'), # (B * G ^ D, U)
            tf.keras.layers.Dense(units=embedding_dim, activation=None, use_bias=False, kernel_initializer='glorot_uniform', bias_initializer=None, name='embed-1'),] # (B * G ^ D, U) => (B * G ^ D, E)
            + [_mmtl.TokenizeBlock(left_axis=-2, right_axis=-1, token_dim=token_dim, latent_dim=latent_dim, attention=attention, name='tokenize' + (__i + 1) * '-4') for __i in range(depth)]) # (B * G ^ i, E) => (B * G ^ (i-1), E)

    def call(self, x: tf.Tensor) -> tf.Tensor:
        return self._encoder(x)

class Decoder(tf.keras.models.Model):
    def __init__(self, depth: int, token_dim: int, encoding_dim: int, embedding_dim: int, latent_dim: int, batch_dim: int=None, attention: bool=False, **kwargs) -> None:
        super(Decoder, self).__init__(**kwargs)
        self._decoder = tf.keras.Sequential(
            [tf.keras.Input(shape=(latent_dim,), batch_size=batch_dim, name='input')] # (B, E)
            + [_mmtl.DetokenizeBlock(token_dim=token_dim, embedding_dim=embedding_dim, attention=attention, name='detokenize' + (depth - __i) * '-4') for __i in range(depth)] # (B * G ^ i, E) => (B * G ^ (i+1), E)
            + [_mmtl.HeadBlock(encoding_dim=encoding_dim, name='project-head')]) # (B * G ^ D, E) => (B * G ^ D, U)

    def call(self, x: tf.Tensor) -> tf.Tensor:
        return self._decoder(x)

class AutoEncoder(tf.keras.models.Model):
    def __init__(self, depth: int, token_dim: int, encoding_dim: int, embedding_dim: int, latent_dim: int, batch_dim: int=None, attention: bool=False, **kwargs) -> None:
        super(AutoEncoder, self).__init__(**kwargs)
        self._encoder = Encoder(depth=depth, token_dim=token_dim, encoding_dim=encoding_dim, embedding_dim=embedding_dim, latent_dim=latent_dim, batch_dim=batch_dim, attention=attention)
        self._decoder = Decoder(depth=depth, token_dim=token_dim, encoding_dim=encoding_dim, embedding_dim=embedding_dim, latent_dim=latent_dim, batch_dim=batch_dim, attention=attention)

    def call(self, x: tf.Tensor) -> tf.Tensor:
        return self._decoder(self._encoder(x))

# INIT ########################################################################

# (B, 4) => (B, 4, 256) => (B, 1024) => (B, 256)
# (B, 256) => (B, 1024) => (B, 4, 256) => (B, 4, 256) => (B, 4, 256)
MODEL = AutoEncoder(depth=N_DEPTH, token_dim=N_TOKEN_DIM, encoding_dim=N_ENCODING_DIM, embedding_dim=N_EMBEDDING_DIM, latent_dim=N_LATENT_DIM, batch_dim=None, attention=False)

# compile
MODEL.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=R_MAX),
    loss=tf.keras.losses.CategoricalCrossentropy(from_logits=False, label_smoothing=0., axis=-1, reduction=tf.keras.losses.Reduction.SUM_OVER_BATCH_SIZE, name='loss'),
    metrics=['accuracy'])

# SAVE ########################################################################

# log path
LOGPATH = os.path.join('.logs/', VERSION, datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
SUMMARY = tf.summary.create_file_writer(LOGPATH)

# called during training
tb_callback = tf.keras.callbacks.TensorBoard(log_dir=LOGPATH)

# LEARNING RATE ###############################################################

lr_callback = tf.keras.callbacks.LearningRateScheduler(functools.partial(_mto.learning_rate_hokusai, lr_min=R_MIN, lr_max=R_MAX, lr_exp=R_EXP, rampup=N_EPOCHS_RAMPUP, sustain=N_EPOCHS_SUSTAIN), verbose=True)

# PREPROCESS ##################################################################

DATA = {__l: _mmtp.preprocess(dataset=__d, key='context', layer_count=N_DEPTH, group_size=N_TOKEN_DIM, sample_size=N_SAMPLE, flatten=True) for __l, __d in DATA.items()}

# TRAIN #######################################################################

# TRAINING_HISTORY = MODEL.fit(
#     x=DATA['en'],
#     batch_size=N_BATCH,
#     epochs=N_EPOCHS,
#     validation_split=None,
#     validation_data=DATA['zh'], # full of glyphs
#     validation_freq=list(range(1, N_EPOCHS + 1, N_EPOCHS // 8)),
#     verbose=2,
#     callbacks=[lr_callback, tb_callback])

# SAMPLES #####################################################################

SAMPLES = {}
TOKENS = {1: {}, 4: {}, 16: {}}
EMBEDDINGS = {1: {}, 4: {}, 16: {}}

for __l in DATA:
    # compute predictions
    __i = iter(DATA[__l]) # iterate over batches of samples
    __x = next(__i)[0] # take input only
    __o = MODEL(__x)
    # sample predictions (inputs, outputs)
    SAMPLES[__l] = (__x, __o)
    # unique 1-tokens (characters)
    TOKENS[1][__l] = _mmtp.chunk(seq=_mmtp.postprocess(__x), size=1, repeats=False)
    # unique 4-tokens
    TOKENS[4][__l] = _mmtp.chunk(seq=_mmtp.postprocess(__x), size=4, repeats=False)
    # unique 4x4-tokens
    TOKENS[16][__l] = _mmtp.chunk(seq=_mmtp.postprocess(__x), size=16, repeats=False)

TOKENS[1]['all'] = list(set(__t for _, __s in TOKENS[1].items() for __t in __s))
TOKENS[4]['all'] = list(set(__t for _, __s in TOKENS[4].items() for __t in __s))
TOKENS[16]['all'] = list(set(__t for _, __s in TOKENS[16].items() for __t in __s))

# EMBEDDINGS ##################################################################

for __l, __s in TOKENS[1].items():
    # re-encode without token repeats
    __token_x = tf.one_hot(indices=_mmtp._tokenize_scalar(text=''.join(__s), layer_count=N_DEPTH, group_size=4, flatten=True), depth=256, axis=-1)
    # embed
    EMBEDDINGS[1][__l] = MODEL._encoder._encoder.layers[1](MODEL._encoder._encoder.layers[0](__token_x))[:len(__s)]

for __l, __s in TOKENS[4].items():
    # re-encode without token repeats
    __token_x = tf.one_hot(indices=_mmtp._tokenize_scalar(text=''.join(__s), layer_count=N_DEPTH, group_size=4, flatten=True), depth=256, axis=-1)
    # embed
    EMBEDDINGS[4][__l] = MODEL._encoder._encoder.layers[2](MODEL._encoder._encoder.layers[1](MODEL._encoder._encoder.layers[0](__token_x)))[:len(__s)]

for __l, __s in TOKENS[16].items():
    # re-encode without token repeats
    __token_x = tf.one_hot(indices=_mmtp._tokenize_scalar(text=''.join(__s), layer_count=N_DEPTH, group_size=4, flatten=True), depth=256, axis=-1)
    # embed
    EMBEDDINGS[16][__l] = MODEL._encoder(__token_x)[:len(__s)]

# SAVE ########################################################################

_mti.write(data=[__c + _mti.label(__c) for __c in TOKENS[1]['all']], path='./metadata.1.tsv', tsv=False)
_mti.write(data=EMBEDDINGS[1]['all'].numpy(), path='./embeddings.1.tsv', tsv=True)

_mti.write(data=[__c + _mti.label(__c) for __c in TOKENS[4]['all']], path='./metadata.4.tsv', tsv=False)
_mti.write(data=EMBEDDINGS[4]['all'].numpy(), path='./embeddings.4.tsv', tsv=True)

_mti.write(data=[__c + _mti.label(__c) for __c in TOKENS[16]['all']], path='./metadata.16.tsv', tsv=False)
_mti.write(data=EMBEDDINGS[16]['all'].numpy(), path='./embeddings.16.tsv', tsv=True)

# TEST ########################################################################

__x = tf.one_hot(indices=_tokenize_scalar(text=TEST, layer_count=N_DEPTH, group_size=4, flatten=True), depth=256, axis=-1)
__e = MODEL._encoder(__x)
__p = MODEL(__x)
__y = postprocess(__p)

print(__sample)
print(__y)
print(sum(__l == __r for __l, __r in zip(__sample, __y)) / len(__sample))
