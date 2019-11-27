# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 12:59:31 2019

@author: cegbh
"""

import numpy as np
import tensorflow as tf

# can be edited (to anything larger than vocab size) if encoding of vocab already uses 0, 1
END_TOKEN = 0
START_TOKEN = 1


class PointerNet(object):
    def __init__(self, n_pointers=2, batch_size=100, seq_length=45, learning_rate=0.001,
                 cell=tf.contrib.rnn.LSTMCell, n_layers=1, n_units=256, num_filters=100,
                 filter_sizes=[3,4,5]):
        """Creates TensorFlow graph of a pointer network.
        Args:
            n_pointers (int):      Number of pointers to generate.
            batch_size (int) :     Batch size for training/inference.
            seq_length (int):      Maximum sequence length of inputs to encoder.
            learning_rate (float): Learning rate for Adam optimizer.
            cell (method):         Method to create single RNN cell.
            n_layers (int):        Number of layers in RNN (assumed to be the same for encoder & decoder).
            n_units (int):         Number of units in RNN cell (assumed to be the same for all cells).
        """

        with tf.variable_scope('inputs'):
            # integer-encoded input passages (e.g. 'She went home' -> [2, 3, 4])
            self.encoder_inputs = tf.placeholder(tf.int32, [batch_size, seq_length])
            # actual non-padded length of each input passages; used for dynamic unrolling
            # (e.g. ['She went home', 'She went to the station'] -> [3, 5])
            self.input_lengths = tf.placeholder(tf.int32, [batch_size])

        with tf.variable_scope('outputs'):
            # pointer(s) to answer: (e.g. 'She went home' -> [2])
            self.pointer_labels = tf.placeholder(tf.int32, [batch_size, n_pointers])
            start_tokens = tf.constant(START_TOKEN, shape=[batch_size], dtype=tf.int32)
            # outputs of decoder are the word 'pointed' to by each pointer
            self.decoder_labels = tf.stack([tf.gather(inp, ptr) for inp, ptr in
                                           list(zip(tf.unstack(self.encoder_inputs), tf.unstack(self.pointer_labels)))])
            # inputs to decoder are inputs shifted over by one, with a <start> token at the front
            self.decoder_inputs = tf.concat([tf.expand_dims(start_tokens, 1), self.decoder_labels], 1)
            # output lengths are equal to the number of pointers
            self.output_lengths = tf.constant(n_pointers, shape=[batch_size])
            '''
        with tf.variable_scope('embeddings'):
            # load pre-trained GloVe embeddings
            word_matrix = tf.constant(np.load('./data/word_matrix.npy'), dtype=tf.float32)
            self.word_matrix = tf.Variable(word_matrix, trainable=True, name='word_matrix')
            # lookup embeddings of inputs & decoder inputs
            self.input_embeds = tf.nn.embedding_lookup(self.word_matrix, self.encoder_inputs)
            self.output_embeds = tf.nn.embedding_lookup(self.word_matrix, self.decoder_inputs)
            '''
        # Embedding layer
        with tf.device('/cpu:0'), tf.name_scope("embedding"):
            self.W = tf.Variable(
                tf.random_uniform([vocab_size, seq_length], -1.0, 1.0),
                name="W")
            self.embedded_chars = tf.nn.embedding_lookup(self.W, self.input_x)
            self.embedded_chars_expanded = tf.expand_dims(self.embedded_chars, -1)

        # Create a convolution + maxpool layer for each filter size
        pooled_outputs = []
        for i, filter_size in enumerate(filter_sizes):
            with tf.name_scope("conv-maxpool-%s" % filter_size):
                # Convolution Layer
                filter_shape = [filter_size, seq_length, 1, num_filters]
                W = tf.Variable(tf.truncated_normal(filter_shape, stddev=0.1), name="W")
                b = tf.Variable(tf.constant(0.1, shape=[num_filters]), name="b")
                conv = tf.nn.conv2d(
                    self.embedded_chars_expanded,
                    W,
                    strides=[1, 1, 1, 1],
                    padding="VALID",
                    name="conv")
                # Apply nonlinearity
                h = tf.nn.relu(tf.nn.bias_add(conv, b), name="relu")
                # Maxpooling over the outputs
                pooled = tf.nn.max_pool(
                    h,
                    ksize=[1, seq_length - filter_size + 1, 1, 1],
                    strides=[1, 1, 1, 1],
                    padding='VALID',
                    name="pool")
                pooled_outputs.append(pooled)

        # Combine all the pooled features
        num_filters_total = num_filters * len(filter_sizes)
        self.h_pool = tf.concat(pooled_outputs, 3)
        self.input_embeds = tf.reshape(self.h_pool, [-1, num_filters_total])
        
        with tf.variable_scope('encoder'):
            
            fw_enc_cell = cell(n_units)
            bw_enc_cell = cell(n_units)
            (encoder_outputs, (fw_st, bw_st)) = tf.nn.bidirectional_dynamic_rnn(fw_enc_cell, bw_enc_cell, self.input_embeds, dtype=tf.float32, sequence_length=self.input_lengths, swap_memory=True)
            self.encoder_outputs = tf.concat(axis=2, values=encoder_outputs) # concatenate the forwards and backwards states
            #self.encoder_outputs, _ = tf.nn.dynamic_rnn(enc_cell, self.input_embeds, self.input_lengths, dtype=tf.float32)

        with tf.variable_scope('attention'):
            attention = tf.contrib.seq2seq.BahdanauAttention(n_units, self.encoder_outputs,
                                                             memory_sequence_length=self.input_lengths)

        with tf.variable_scope('decoder'):
            helper = tf.contrib.seq2seq.GreedyEmbeddingHelper(self.word_matrix, start_tokens, END_TOKEN)
            if n_layers > 1:
                dec_cell = tf.contrib.rnn.MultiRNNCell([cell(n_units) for _ in range(n_layers)])
            else:
                dec_cell = cell(n_units)
            attn_cell = tf.contrib.seq2seq.AttentionWrapper(dec_cell, attention, alignment_history=True)
            out_cell = tf.contrib.rnn.OutputProjectionWrapper(attn_cell, word_matrix.shape[0] - 2)
            decoder = tf.contrib.seq2seq.BasicDecoder(out_cell, helper, out_cell.zero_state(batch_size, tf.float32))
            self.decoder_outputs, dec_state, _ = tf.contrib.seq2seq.dynamic_decode(decoder, maximum_iterations=n_pointers)

        with tf.variable_scope('pointers'):
            # tensor of shape (# pointers, batch size, max. input sequence length)
            self.pointer_prob = tf.reshape(dec_state.alignment_history.stack(), [n_pointers, batch_size, seq_length])
            self.pointers = tf.unstack(tf.argmax(self.pointer_prob, axis=2, output_type=tf.int32))

        with tf.variable_scope('loss'):
            loss = tf.zeros(())
            pointers = tf.unstack(self.pointer_prob)
            labels = tf.unstack(self.pointer_labels, axis=1)

            equal = []
            for i in range(n_pointers):
                loss += tf.nn.sparse_softmax_cross_entropy_with_logits(labels=labels[i], logits=pointers[i])
                equal.append(tf.equal(self.pointers[i], labels[i]))
            self.loss = tf.reduce_mean(loss)
            self.correct = tf.cast(tf.stack(equal), tf.float32)
            self.all_correct = tf.cast(tf.equal(tf.reduce_sum(self.correct, axis=0), n_pointers), tf.float32)
            self.exact_match = tf.reduce_mean(self.all_correct)

        with tf.variable_scope('training'):
            self.train_step = tf.train.AdamOptimizer(learning_rate).minimize(self.loss)


if __name__ == '__main__':
    model = PointerNet()