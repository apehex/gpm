import hashlib

import tensorflow as tf

# DEFAULT META #################################################################

N_CONTEXT_DIM = 8
N_EMBEDDING_DIM = 128

# HYPER PARAMETERS #############################################################

def seed(key: str) -> int:
    __hash = hashlib.sha256(string=key.encode('utf-8')).hexdigest()
    return int(__hash[:8], 16) # take the first 4 bytes: the seed is lower than 2 ** 32

# MODEL ########################################################################

def create(
    seed: int,
    n_input_dim: int,
    n_output_dim: int,
    n_context_dim: int=N_CONTEXT_DIM,
    n_embedding_dim: int=N_EMBEDDING_DIM,
) -> tf.keras.Model:
    __model = tf.keras.Sequential()
    # initialize the weights
    __embedding_init = tf.keras.initializers.GlorotNormal(seed=seed)
    __dense_init = tf.keras.initializers.GlorotNormal(seed=(seed ** 2) % (2 ** 32)) # different values
    # embedding
    __model.add(tf.keras.layers.Embedding(input_dim=n_input_dim, output_dim=n_embedding_dim, embeddings_initializer=__embedding_init, name='embedding'))
    # head
    __model.add(tf.keras.layers.Reshape(target_shape=(n_context_dim * n_embedding_dim,), name='reshape'))
    __model.add(tf.keras.layers.Dense(units=n_output_dim, activation='tanh', use_bias=False, kernel_initializer=__dense_init, name='head'))
    __model.add(tf.keras.layers.Softmax(axis=-1, name='softmax'))
    # compile
    __model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss=tf.keras.losses.CategoricalCrossentropy(from_logits=False, label_smoothing=0., axis=-1, reduction=tf.keras.losses.Reduction.SUM_OVER_BATCH_SIZE, name='loss'))
    return __model