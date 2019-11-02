# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 16:29:08 2019

@author: cegbh
"""

import nltk
import string
from sklearn.decomposition.truncated_svd import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import Normalizer
from sklearn.metrics.pairwise import linear_kernel

class SimilarEmail:
    
    def __init__(self, email_body_list):
        self.corpus = []
        self.stopword_list = nltk.corpus.stopwords.words('english')
        self.punctuations_list = list(string.punctuation)
        self.data = email_body_list
        self.createCorpus()
      
    def createCorpus(self):
        for email in self.data:
            token_list = self.getTokens(email)
            tokens = ' '.join(map(str, token_list))
            self.corpus.append(tokens)

      
    def getTokens(self, email_body):
        token_list = nltk.word_tokenize(email_body)
        token_list = [word.lower() for word in token_list if (word not in self.punctuations_list)]
        token_list = [word.lower() for word in token_list if word not in self.stopword_list]
        return token_list
    
    def addEmailToModel(self, email_body):
        if email_body is not None:
            token_list = self.getTokens(email_body)
            tokens = ' '.join(map(str, token_list))
            self.corpus.append(tokens)

        
    def buildModel(self):
        tfidfModel = TfidfVectorizer().fit_transform(self.corpus)
        lsa = TruncatedSVD(n_components=200)
        self.Model = lsa.fit_transform(tfidfModel)
        self.Model = Normalizer(copy=False).fit_transform(self.Model)
         
    def computeSimilarity(self, email_body):
        self.addEmailToModel(email_body)
        self.buildModel()
        try:
            query = -1
            query = [self.Model[query]]
            cosine_similarities = linear_kernel(query, self.Model).flatten()
            index = cosine_similarities.argsort()[-2]
            return index, cosine_similarities[index]      
        except:
            print("Entering exception")
            return None, None
        
    def getSimilarEmail(self, email_body):
        index, sims = self.computeSimilarity(email_body)
        if index == None and sims == None:
            print("Error with cosine calculation. Exiting")
            exit(0)
        similarEmail = self.data[index]
        return similarEmail
    
if __name__ == '__main__':
    file = open(r'../Dataset/Test.txt', 'r')
    data = file.read()
    file.close()
    data_list = data.split('\n')
    se = SimilarEmail(data_list)
    new_text = "A laptop computer (also shortened to just laptop; or called a notebook computer) is a small, portable personal computer (PC) with a \"clamshell\" form factor, typically having a thin LCD or LED computer screen mounted on the inside of the upper lid of the clamshell and an alphanumeric keyboard on the inside of the lower lid. The clamshell is opened up to use the computer. Laptops are folded shut for transportation, and thus are suitable for mobile use.[1] Its name comes from lap, as it was deemed to be placed on a person's lap when being used. Although originally there was a distinction between laptops and notebooks (the former being bigger and heavier than the latter), as of 2014, there is often no longer any difference.[2] Laptops are commonly used in a variety of settings, such as at work, in education, for playing games, Internet surfing, for personal multimedia, and general home computer use."
    print(se.getSimilarEmail(new_text))
    violin_text = "The violin, sometimes known as a fiddle, is a wooden string instrument in the violin family. Most violins have a hollow wooden body. It is the smallest and highest-pitched instrument in the family in regular use. Smaller violin-type instruments exist, including the violino piccolo and the kit violin, but these are virtually unused. The violin typically has four strings, usually tuned in perfect fifths with notes G3, D4, A4, E5, and is most commonly played by drawing a bow across its strings, though it can also be played by plucking the strings with the fingers (pizzicato) and by striking the strings with the wooden side of the bow (col legno)."
    print(se.getSimilarEmail(violin_text))
     
         
        