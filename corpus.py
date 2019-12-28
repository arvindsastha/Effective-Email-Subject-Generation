# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 00:22:22 2019

@author: cegbh
"""

import nltk
import string
import numpy as np
import pandas as pd

from gensim.models.keyedvectors import KeyedVectors
import tensorflow_hub as hub

from keras.layers import Embedding
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.layers import Conv1D, MaxPooling1D
from keras.layers import Concatenate
from keras.models import Input, Model
from keras.layers import Dense, Flatten, Dropout
from keras.layers.core import Reshape
from keras import regularizers


EMBEDDING_DIM = 300
MAX_WORDS = 200000
MAX_SEQUENCE_LENGTH = 200

class Corpus:
    
    def __init__(self, email_body_list):
        self.corpus = []
        self.all_tokens = []
        self.stopword_list = nltk.corpus.stopwords.words('english')
        self.punctuations_list = list(string.punctuation)
        self.data = email_body_list
        self.createCorpus()
        
    def createCorpus(self):
        for email in self.data:
            token_list = self.getTokens(email)
            self.all_tokens.append(token_list)
            tokens = ' '.join(map(str, token_list))
            self.corpus.append(tokens)
    
    def getTokens(self, email_body):
        token_list = nltk.word_tokenize(email_body)
        token_list = [word.lower() for word in token_list if (word not in self.punctuations_list)]
        token_list = [word.lower() for word in token_list if word not in self.stopword_list]
        return token_list
    
    def getCorpus(self):
        return self.corpus
    
    def getVocab(self):
        all_training_words = [word for tokens in self.all_tokens for word in tokens]
        self.vocab = sorted(list(set(all_training_words)))
        return self.vocab, len(self.vocab)
    
    def getMaxSeqLength(self):
        seqLength = max(len(tokens) for tokens in self.all_tokens)
        return seqLength
    

class EncoderCNN:
    def __init__(self):
        print("Initializing the Encoder")
        
    def preProcessing(self, email_body_list):
        tokenizer = Tokenizer(num_words=MAX_WORDS,filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n\'', lower=True)
        tokenizer.fit_on_texts(email_body_list)
        sequences_train = tokenizer.texts_to_sequences(email_body_list)
        word_index = tokenizer.word_index
        X_train = pad_sequences(sequences_train)
        return tokenizer,word_index,X_train
        
        
    def load_pretrained_word2vec(self, word_index):
        word_vectors = KeyedVectors.load_word2vec_format('../Dataset/GoogleNews-vectors-negative300.bin', binary=True)
        vocabulary_size=min(len(word_index)+1,MAX_WORDS)
        embedding_matrix = np.zeros((vocabulary_size, EMBEDDING_DIM))
        for word, i in word_index.items():
            if i>=MAX_WORDS:
                continue
            try:
                embedding_vector = word_vectors[word]
                embedding_matrix[i] = embedding_vector
            except KeyError:
                embedding_matrix[i]=np.random.normal(0,np.sqrt(0.25),EMBEDDING_DIM)
        del(word_vectors)
        embedding_layer = Embedding(vocabulary_size,EMBEDDING_DIM,weights=[embedding_matrix],trainable=True)
        return embedding_layer

    def ConvNet(self, embedding_layer, max_sequence_length, num_words, embedding_dim, trainable=False):
        #hub_layer = hub.KerasLayer("https://tfhub.dev/google/nnlm-en-dim128/2",
         #                  input_shape=[], dtype=tf.string)
        sequence_input = Input(shape=(max_sequence_length,), dtype='int32')
        embedded_sequences = embedding_layer(sequence_input)
    
        # Yoon Kim model (https://arxiv.org/abs/1408.5882)
        convs = []
        filter_sizes = [3,4,5]
        num_filters = 100
    
        for filter_size in filter_sizes:
            l_conv = Conv1D(filters=num_filters, kernel_size=filter_size, activation='relu')(embedded_sequences)
            l_pool = MaxPooling1D(pool_size=3)(l_conv)
            convs.append(l_pool)
    
        l_merge = Concatenate(axis = 1)(convs)
        model = Model(sequence_input, l_merge)
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['acc'])
        return model

if __name__ == '__main__':
    file = open(r'../Dataset/Test.txt', 'r')
    data = file.read()
    file.close()
    data_list = data.split('\n')
    corpus_object = Corpus(data_list)
    
    
    df = pd.read_csv(r'Sentence_Subject_labels.csv')
    sentence_list = df['Sentence']
    labels = df['Label']
    ecnn = EncoderCNN()
    tokenizer,word_index,X_train = ecnn.preProcessing(sentence_list)
    embedding_layer = ecnn.load_pretrained_word2vec(word_index)
    model = ecnn.ConvNet(embedding_layer, MAX_SEQUENCE_LENGTH, len(word_index)+1, EMBEDDING_DIM, False)
    print(model.summary())