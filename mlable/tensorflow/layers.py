import numpy as np
import tensorflow as tf

import mlable.tensorflow.initializers as _mti

# NORMALIZATION ###############################################################

class BatchNormalization(tf.keras.layers.Layer):
    def __init__(
        self,
        axis=0,
        momentum=0.99,
        epsilon=0.001,
        **kwargs
    ):
        super(BatchNormalization, self).__init__(**kwargs)
        self._axis = axis
        self._momentum = momentum
        self._epsilon = epsilon
        self._mean = None
        self._stddev = None
        self._gain = None
        self._bias = None

    def build(self, shape: tuple):
        # shape
        __axis = self._axis % len(shape) # positive index even when the axis is specified negatively, like -2
        __shape = [__d for __i, __d in enumerate(shape) if __i != __axis]
        # values
        __mean_init = _mti.SmallNormal()
        __stddev_init = _mti.SmallNormal()
        __gain_init = _mti.SmallNormal()
        __bias_init = _mti.SmallNormal()
        # tensors
        self._mean = self.add_weight("mean", shape=__shape, initializer=__mean_init)
        self._stddev = self.add_weight("stddev", shape=__shape, initializer=__stddev_init)
        self._gain = self.add_weight("gain", shape=__shape, initializer=__gain_init)
        self._bias = self.add_weight("bias", shape=__shape, initializer=__bias_init)

    def call(self, inputs: tf.Tensor, training: bool=True, **kwargs):
        if training:
            # current values
            __batch_mean = tf.math.reduce_mean(inputs, axis=self._axis, keepdims=True)
            __batch_stddev = tf.math.reduce_std(inputs, axis=self._axis, keepdims=True)
            # update parameters
            self._mean = tf.stop_gradient(self._momentum * self._mean + (1. - self._momentum) * __batch_mean)
            self._stddev = tf.stop_gradient(self._momentum * self._stddev + (1. - self._momentum) * __batch_stddev)
        # normalize
        __normalized = tf.math.divide(inputs - self._mean, self._stddev + self._epsilon)
        # scale
        return tf.math.multiply(self._gain, __normalized) + self._bias

class LayerNormalization(tf.keras.layers.Layer):
    def __init__(
        self,
        axis=-1,
        momentum=0.99,
        epsilon=0.001,
        **kwargs
    ):
        super(BatchNormalization, self).__init__(**kwargs)
        self._axis = axis
        self._momentum = momentum
        self._epsilon = epsilon
        self._mean = None
        self._stddev = None
        self._gain = None
        self._bias = None

    def build(self, shape: tuple):
        # shape
        __axis = self._axis % len(shape) # positive index even when the axis is specified negatively, like -2
        __shape = [__d for __i, __d in enumerate(shape) if __i != __axis]
        # values
        __mean_init = _mti.SmallNormal()
        __stddev_init = _mti.SmallNormal()
        __gain_init = _mti.SmallNormal()
        __bias_init = _mti.SmallNormal()
        # tensors
        self._mean = self.add_weight("mean", shape=__shape, initializer=__mean_init)
        self._stddev = self.add_weight("stddev", shape=__shape, initializer=__stddev_init)
        self._gain = self.add_weight("gain", shape=__shape, initializer=__gain_init)
        self._bias = self.add_weight("bias", shape=__shape, initializer=__bias_init)

    def call(self, inputs: tf.Tensor, training: bool=True, **kwargs):
        if training:
            # current values
            __layer_mean = tf.math.reduce_mean(inputs, axis=self._axis, keepdims=True)
            __layer_stddev = tf.math.reduce_std(inputs, axis=self._axis, keepdims=True)
            # update parameters
            self._mean = tf.stop_gradient(self._momentum * self._mean + (1. - self._momentum) * __layer_mean)
            self._stddev = tf.stop_gradient(self._momentum * self._stddev + (1. - self._momentum) * __layer_stddev)
        # normalize
        __normalized = tf.math.divide(inputs - self._mean, self._stddev + self._epsilon)
        # scale
        return tf.math.multiply(self._gain, __normalized) + self._bias

# REGULARIZATION ##############################################################

# dropout

# LINEAR ######################################################################

class Dense(tf.keras.layers.Layer):
    def __init__(
        self,
        units: int,
        use_bias: bool=True,
        **kwargs
    ):
        super(Dense, self).__init__(**kwargs)
        self._units = units
        self._biased = use_bias
        self._kernel = None
        self._bias = None

    def build(self, shape: tuple):
        # kernel
        __kernel_init = _mti.SmallNormal()
        self._kernel = self.add_weight("kernel", shape=[int(shape[-1]), self._units], initializer=__kernel_init)
        # bias
        if self._biased:
            __bias_init = _mti.SmallNormal()
            self._bias = self.add_weight("bias", shape=[self._units], initializer=__bias_init)

    def call(self, inputs: tf.Tensor, **kwargs):
        return tf.matmul(inputs, self._kernel) + self._bias if (self._biased and self._bias is not None) else tf.matmul(inputs, self._kernel)

# QUADRATIC ###################################################################

class Attention(tf.keras.layers.Layer):
    def __init__(
        self,
        head_dim: int,
        head_count: int=1,
        **kwargs
    ):
        super(Attention, self).__init__(**kwargs)
        self._time_dim = None
        self._head_dim = head_dim
        self._head_count = head_count
        self._key = None
        self._query = None
        self._value = None

    def build(self, shape: tuple) -> None:
        self._time_dim = list(shape)[-1]
        # init
        __key_init = _mti.SmallNormal()
        __query_init = _mti.SmallNormal()
        __value_init = _mti.SmallNormal()
        # kernels
        self._key = self.add_weight("key", shape=[int(shape[-1]), self._head_dim], initializer=__key_init)
        self._query = self.add_weight("query", shape=[int(shape[-1]), self._head_dim], initializer=__query_init)
        self._value = self.add_weight("value", shape=[int(shape[-1]), self._head_dim], initializer=__value_init)

    def call(self, inputs: tf.Tensor, **kwargs) -> tf.Tensor:
        # transpose the last two axes
        __perm = range(len(list(inputs.shape)))
        __perm[-1] = len(__perm) - 2
        __perm[-2] = len(__perm) - 1
        # key
        __k = tf.matmul(inputs, self._key)
        # query
        __q = tf.matmul(inputs, self._query)
        # weight
        __w = tf.matmul(__k, tf.transpose(__q, perm=__perm)) / tf.math.sqrt(float(self._head_dim))
        # mask
        __m = tf.linalg.band_part(tf.ones((self._time_dim, self._time_dim)), num_lower=0, num_upper=-1) - tf.linalg.diag(self._time_dim * [1.])
        __u = tf.where(__m == 1., -np.inf, 0.)
        __l = tf.linalg.band_part(__w, num_lower=-1, num_upper=0)
        # probabilities
        __w = tf.nn.softmax(__u + __l, axis=-1)
        # value
        return tf.matmul(__w, self._value)

# EMBEDDING ###################################################################

class Embedding(tf.keras.layers.Layer):
    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        add_position: bool=False,
        **kwargs
    ):
        super(Embedding, self).__init__(**kwargs)
        self._add_position = add_position
        self._input_dim = input_dim
        self._output_dim = output_dim
        self._time_dim = None
        self._content_kernel = None
        self._position_kernel = None

    def build(self, shape: tuple):
        # content
        __content_kernel_init = _mti.SmallNormal()
        self._content_kernel = self.add_weight("content-kernel", shape=[self._input_dim, self._output_dim], initializer=__content_kernel_init)
        # position
        self._time_dim = list(shape)[-1]
        if self._add_position:
            __position_kernel_init = _mti.SmallNormal()
            self._position_kernel = self.add_weight("position-kernel", shape=[self._time_dim, self._output_dim], initializer=__position_kernel_init)

    def call(self, inputs: tf.Tensor, **kwargs):
        # content embedding
        __x = tf.one_hot(indices=inputs, depth=self._input_dim, dtype=tf.dtypes.float32)
        __y = tf.matmul(__x, self._content_kernel)
        # position embedding
        if self._add_position:
            __diag = tf.convert_to_tensor(range(self._time_dim), dtype=tf.dtypes.float32)
            __diag = (__values - tf.math.reduce_mean(__diag)) / tf.math.reduce_std(__diag) # normalize
            __x_pos = tf.linalg.tensor_diag(__diag)
            __y_pos = tf.matmul(__x_pos, self._position_kernel)
            __y = __y + tf.reshape(tensor=__y_pos, shape=[1] + list(__y_pos.shape))
        # overall embedding
        return __y

# RESIDUALS ###################################################################

# ACTIVATION ##################################################################

class Activation(tf.keras.layers.Layer):
    def __init__(
        self,
        function: callable,
        **kwargs
    ):
        super(Activation, self).__init__(**kwargs)
        self._function = function

    def call(self, inputs: tf.Tensor, **kwargs):
        return self._function(inputs)

class Softmax(tf.keras.layers.Layer):
    def __init__(
        self,
        axis: int=-1,
        **kwargs
    ):
        super(Softmax, self).__init__(**kwargs)
        self._axis = axis

    def call(self, inputs: tf.Tensor, **kwargs):
        return tf.nn.softmax(inputs, axis=self._axis)

# RESHAPING ###################################################################

class Merge(tf.keras.layers.Layer):
    def __init__(
        self,
        axis: int,
        n: int,
        **kwargs
    ):
        super(Merge, self).__init__(**kwargs)
        self._axis = axis
        self._n = n

    def call(self, inputs: tf.Tensor, **kwargs):
        __shape = list(inputs.shape)
        __axis0 = self._axis % len(__shape)
        __axis1 = (self._axis + 1) % len(__shape)
        # merge n rows along the given axis
        __shape[__axis0] = inputs.shape[__axis0] // self._n
        __shape[__axis1] = inputs.shape[__axis1] * self._n
        return tf.reshape(inputs, __shape) # tf.squeeze

class Reshape(tf.keras.layers.Layer):
    def __init__(
        self,
        target_shape: tuple,
        **kwargs
    ):
        super(Reshape, self).__init__(**kwargs)
        self._shape = target_shape

    def call(self, inputs: tf.Tensor, **kwargs):
        return tf.reshape(inputs, self._shape)
