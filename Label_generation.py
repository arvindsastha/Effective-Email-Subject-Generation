# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 23:57:49 2019

@author: cegbh
"""
import nltk
from nltk import sent_tokenize
import pandas as pd
#import spacy

def createLabelsForSentence(sentence, subject):
    stopword_list = nltk.corpus.stopwords.words('english')
    #stopword_list = spacy.lang.en.stop_words.STOP_WORDS
    words = nltk.word_tokenize(sentence)
    for word in words:
        if word in subject and word not in stopword_list:
            return 1
    return 0
    
def writeDataFrameToCsv(dataFrame):
    dataFrame.to_csv(r'Sentence_Subject_labels.csv', index = False)    

def preCreateLabels(email_body_list, subject_list):
    email_label_df = pd.DataFrame()
    for i in range(len(email_body_list)):
        email_body = email_body_list[i]
        subject = subject_list[i]
        sentences = sent_tokenize(email_body)
        for sentence in sentences:
            label = createLabelsForSentence(sentence, subject)
            df = pd.DataFrame({"Sentence" : [sentence], "Subject" : [subject], "Label" : [label]})
            email_label_df = email_label_df.append(df)
    writeDataFrameToCsv(email_label_df)

'''    
file = open(r'../Dataset/Test.txt', 'r')
data = file.read()
file.close()
data_list = data.split('\n')
subject_list = ["This motion is typically translated into the motion of a pointer on a display",
                "mechanical levers or electronic switches", "It is played using a keyboard, which is a row of keys (small levers)",
                "Hundreds of sports exist", "artificial intelligence wanted to see"]

preCreateLabels(data_list, subject_list)
'''    
        
        
    