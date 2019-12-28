# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 04:18:14 2019

@author: cegbh
"""
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import umap
import numpy as np
import matplotlib.pyplot as plt
pd.set_option("display.max_colwidth", 200)
from sklearn.manifold import TSNE
import seaborn as sns

vectorizer = TfidfVectorizer(stop_words='english', 
max_features= 1000, # keep top 1000 terms 
max_df = 0.5, 
smooth_idf=True)

file = pd.read_csv('Processed_Email_Dataset.csv')
document_list,titles=list(file['Email_Body']), list(file['Subject'])
X = vectorizer.fit_transform(file['Email_Body'])

print(X.shape) # check shape of the document-term matrix

# SVD represent documents and terms in vectors 
svd_model = TruncatedSVD(n_components=14, algorithm='randomized', n_iter=100, random_state=122)

svd_model.fit(X)

print(len(svd_model.components_))

terms = vectorizer.get_feature_names()

for i, comp in enumerate(svd_model.components_):
    terms_comp = zip(terms, comp)
    sorted_terms = sorted(terms_comp, key= lambda x:x[1], reverse=True)[:7]
    print("Topic "+str(i)+": ")
    for t in sorted_terms:
        print(t[0], end =" ")
    print("")


X_topics = svd_model.fit_transform(X)

embedding = umap.UMAP(n_neighbors=150, min_dist=0.5, random_state=12).fit_transform(X_topics)
N = 3333
colors = np.linspace(0, 1, N)
plt.figure(figsize=(7,5))
plt.scatter(embedding[:, 0], embedding[:, 1], 
c = colors,
s = 10, # size
edgecolor='none'
)
plt.show()

'''
tsne_lsa_model = TSNE(n_components=3, perplexity=50,
                      learning_rate=100, n_iter=2000, verbose=1,
                      random_state=0, angle=0.75)
#tnse = TSNE()
#tsne_lsa_vectors = tnse.fit_transform(X_topics)
#colors = np.random.rand(N)
#X, y = load_digits(return_X_y=True)
#sns.scatterplot(tsne_lsa_vectors[:,0], tsne_lsa_vectors[:,1], hue=y, legend='full', palette=sns.color_palette("hls", 10))

df_subset = pd.DataFrame()
df_subset['tsne-2d-one'] = tsne_lsa_vectors[:,0]
df_subset['tsne-2d-two'] = tsne_lsa_vectors[:,1]
plt.figure(figsize=(16,10))
sns.scatterplot(
    x="tsne-2d-one", y="tsne-2d-two",
    hue="y",
    palette=sns.color_palette("hls", 10),
    data=df_subset,
    legend="full",
    alpha=0.3
)
'''