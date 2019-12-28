# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 18:11:36 2019

@author: cegbh
"""

from sklearn.datasets import fetch_20newsgroups
import pandas as pd
from Similarity_model import SimilarEmail
from corpus import Corpus

'''

dataset = fetch_20newsgroups(shuffle=True, random_state=1, remove=('headers', 'footers', 'quotes'))
documents = dataset.data
len(documents)
news_df = pd.DataFrame({'document':documents})
'''

news_df = pd.read_csv(r'Processed_Email_Dataset.csv')
# removing everything except alphabets`
news_df['clean_doc'] = news_df['Email_Body'].str.replace("[^a-zA-Z#]", " ")

# removing short words
news_df['clean_doc'] = news_df['clean_doc'].apply(lambda x: ' '.join([w for w in x.split() if len(w)>3]))

# make all text lowercase
news_df['clean_doc'] = news_df['clean_doc'].apply(lambda x: x.lower())
from nltk.corpus import stopwords
stop_words = stopwords.words('english')

# tokenization
tokenized_doc = news_df['clean_doc'].apply(lambda x: x.split())

# remove stop-words
tokenized_doc = tokenized_doc.apply(lambda x: [item for item in x if item not in stop_words])

# de-tokenization
detokenized_doc = []
for i in range(len(news_df)):
    t = ' '.join(tokenized_doc[i])
    detokenized_doc.append(t)

news_df['clean_doc'] = detokenized_doc

print(news_df['clean_doc'])

corpus_object = Corpus(news_df['clean_doc'][101:])
se = SimilarEmail(corpus_object, news_df['clean_doc'])
total_text = " "
#new_text = "A laptop computer (also shortened to just laptop; or called a notebook computer) is a small, portable personal computer (PC) with a \"clamshell\" form factor, typically having a thin LCD or LED computer screen mounted on the inside of the upper lid of the clamshell and an alphanumeric keyboard on the inside of the lower lid. The clamshell is opened up to use the computer. Laptops are folded shut for transportation, and thus are suitable for mobile use.[1] Its name comes from lap, as it was deemed to be placed on a person's lap when being used. Although originally there was a distinction between laptops and notebooks (the former being bigger and heavier than the latter), as of 2014, there is often no longer any difference.[2] Laptops are commonly used in a variety of settings, such as at work, in education, for playing games, Internet surfing, for personal multimedia, and general home computer use."
for i in range(100):
    new_text = news_df['clean_doc'][i]
    print(new_text)
    similar_text = se.getSimilarEmail(new_text)
    total_text = total_text + new_text + similar_text + "\n\n\n"
    print(i)
    
with open("data.txt", 'w+') as f:
    f.write(total_text)
    
#se.getModel().show_topics()

'''
embedding = umap.UMAP(n_neighbors=150, min_dist=0.5, random_state=12).fit_transform(se.getModel())
plt.figure(figsize=(7,5))
plt.scatter(embedding[:, 0], embedding[:, 1], c = dataset.target,s = 10, edgecolor='none')
plt.show()
'''
