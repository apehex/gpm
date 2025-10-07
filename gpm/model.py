import functools
import hashlib

import numpy as np

# DEFAULT META #################################################################

N_CONTEXT_DIM = 8
N_EMBEDDING_DIM = 128

# RANDOM GENERATION ############################################################

def seed(key: str) -> int:
    __hash = hashlib.sha256(string=key.encode('utf-8')).hexdigest()
    return int(__hash[:8], 16) # take the first 4 bytes: the seed is lower than 2 ** 32

def glorot(random_gen: np.random.Generator, input_dim: int, output_dim: int):
    __std = np.sqrt(2.0 / float(max(1, input_dim + output_dim)))
    return random_gen.normal(loc=0.0, scale=__std, size=(input_dim, output_dim)).astype(np.float32)

# MODEL ########################################################################

class MlpModel:
    def __init__(self,
        key_str: str,
        n_input_dim: int,
        n_output_dim: int,
        n_context_dim: int = N_CONTEXT_DIM,
        n_embedding_dim: int = N_EMBEDDING_DIM
    ) -> None:
        # control the random weight generation
        __seed = seed(key_str)
        # initialize the weights
        __embedding_init = np.random.default_rng(__seed)
        __dense_init = np.random.default_rng((__seed ** 2) % (2 ** 32)) # different values
        # embedding (I, E)
        self._embed = glorot(__embedding_init, input_dim=n_input_dim, output_dim=n_embedding_dim)
        # dense (C*E, O)
        self._dense = glorot(__dense_init, input_dim=n_context_dim * n_embedding_dim, output_dim=n_output_dim)

    def __call__(self, inputs: np.ndarray, sample: bool=True) -> np.ndarray:
        __logits = self._forward(inputs)
        return self._sample(__logits) if sample else __logits

    def _forward(self, inputs: np.ndarray) -> np.ndarray:
        assert len(inputs.shape) == 2, 'Expected a rank 2 input tensor.'
        # parse shapes
        __batch_dim, __context_dim = tuple(inputs.shape)
        __input_dim, __embed_dim = tuple(self._embed.shape)
        # enforce dtype
        __inputs = inputs.astype(np.int32)
        # embed (B, C) => (B, C, E)
        __outputs = self._embed[__inputs]
        # reshape (B, C, E) => (B, C*E)
        __outputs = __outputs.reshape((__batch_dim, __context_dim * __embed_dim))
        # project (B, C*E) => (B, O)
        return np.matmul(__outputs, self._dense)

    def _sample(self, logits: np.ndarray) -> np.ndarray:
        __rank = len(logits.shape)
        __order = int(logits.shape[-1])
        __shape = (__rank - 1) * (1,) + (__order,)
        # binarize bit by bit
        __bits = (logits > 0.0).astype(np.int32)
        # low endian decoding
        __shift = np.arange(__order).reshape(__shape)
        # reduce the binary vectors in base 2
        return np.sum(np.left_shift(__bits, __shift), axis=-1).astype(np.int32)
