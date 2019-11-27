# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 23:54:30 2019

@author: cegbh
"""

import nltk
import string
from gensim.models import Word2Vec


 # Download data for tokenizer.
from nltk import word_tokenize
class Word2VecModel:
    
    def __init__(self, email_body_list):
        self.stopword_list = nltk.corpus.stopwords.words('english')
        self.punctuations_list = list(string.punctuation)
        self.data = email_body_list
        
    # Pre-processing a document.
    def preProcess(self, doc):
        #Preprocess raw text by tokenising and removing stop-words,special-charaters
        doc = doc.lower()  # Lower the text.
        doc = word_tokenize(doc)  # Split into words.
        doc = [w for w in doc if not w in self.stopword_list]  # Remove stopwords.
        doc = [w for w in doc if w.isalpha()]  # Remove numbers and punctuation.
        return doc
    
    # Train a word2vec model with default vector size of 100
    def trainWord2Vec(self, vector_size=128, model_name="preTrainedWord2Vec"):
        #Trains a word2vec model on the preprocessed data and saves it .
        if not train_data:
            print("Error loading training data")
            return
        w2v_corpus = [self.preProcess(self.data[i]) for i in range(len(self.data))]
        self.model = Word2Vec(w2v_corpus, size=vector_size)
        self.model.save(model_name)
        print("Model Created Successfully")
    
    # Load the Model
    def loadModel(self, path = "preTrainedWord2Vec"):
        #loads the stored  word2vec model
        return self.model

if __name__ == "__main__":
    train_data = r""
    word2vec_model = Word2VecModel(train_data)
    word2vec_model.trainWord2Vec()
    