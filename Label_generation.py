# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 23:57:49 2019

@author: cegbh
"""
import nltk
import pandas as pd
import re
#import spacy

def createLabelsForSentence(sentence, subject):
    stopword_list = nltk.corpus.stopwords.words('english')
    #stopword_list = spacy.lang.en.stop_words.STOP_WORDS
    words = nltk.word_tokenize(sentence)
    word_count = 0
    for word in words:
        if word in subject and word not in stopword_list:
            word_count = word_count + 1
    return word_count
    
def writeDataFrameToCsv(dataFrame):
    #dataFrame.to_csv(r'Sentence_Subject_labels.csv', index = False)    
    dataFrame.to_csv(r'cleaned_emails.csv', index = False)    

def preCreateLabels(email_body_list, subject_list):
    email_label_df = pd.DataFrame()
    final_list_sentences= []
    final_labels_1 = []
    final_labels_2 = []
    subjects = []
    
    for i in range(len(email_body_list)):
        email_body = email_body_list[i]
        subject = subject_list[i]
        subject = str(subject) 
        #if not re.search('[a-zA-Z]', email_body) or not re.search('[a-zA-Z]', subject):
        #    continue
        email_body = str(email_body)
        sentences = email_body.split(".")
        #sentences = sent_tokenize(email_body)
        passage = ""
        labels = []
        
        for sentence in sentences:
          if re.search('[a-zA-Z]', sentence):
            #passage = passage + "$$$" + sentence
            passage = passage + sentence + ". "
            labels.append(createLabelsForSentence(sentence, subject))
          #df = pd.DataFrame({"Sentence" : [sentence], "Subject" : [subject], "Label" : [label]})
          #email_label_df = email_label_df.append(df)
        
        if passage:
          print(passage)
          print(labels)
          print(subject)
          
          if labels:
            max_1 = labels[0]
            max_1_index = 0
            
            for i in range(len(labels)):
              if labels[i] > max_1:
                max_1 = labels[i]
                max_1_index = i
                
            max_2 = 0
            max_2_index = -1
            for i in range(len(labels)):
              if labels[i] > max_2 and labels[i] <= max_1 and i != max_1_index:
                max_2 = labels[i]
                max_2_index = i
                
            print(max_1_index)
            print(max_2_index)
            print("--------------------------------------")

            if max_1_index != -1:
              final_labels_1.append(max_1_index)
              final_labels_2.append(max_2_index)
              final_list_sentences.append(passage)
              subjects.append(subject)
              
    email_label_df["Email_Body"] = final_list_sentences
    email_label_df["Label 1"] = final_labels_1
    email_label_df["Label 2"] = final_labels_2
    email_label_df["Subject"] = subjects
    
    print(email_label_df)
    writeDataFrameToCsv(email_label_df)

emails_and_subjects = pd.read_csv("emails_and_subject.csv")
preCreateLabels(emails_and_subjects["Email Body"], emails_and_subjects["Subject"])


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
        
        
    
