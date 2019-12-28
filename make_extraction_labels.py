"""produce the dataset with (psudo) extraction label"""
import os
from os.path import exists, join
import json
from time import time
from datetime import timedelta
import multiprocessing as mp
import pandas as pd

from cytoolz import curry, compose

from utils import count_data
from metric import compute_rouge_l

 

try:
    #DATA_DIR = os.environ['DATA']
    DATA_DIR = './email_dataset/finished_files'
except KeyError:
    print('please use environment variable to specify data directories')


def _split_words(texts):
    return map(lambda t: t.split(), texts)

def get_extract_label(art_sents, abs_sents):
    """ greedily match summary sentences to article sentences"""
    extracted = []
    scores = []
    indices = list(range(len(art_sents)))
    for abst in abs_sents:
        rouges = list(map(compute_rouge_l(reference=abst, mode='r'),
                          art_sents))
        ext = max(indices, key=lambda i: rouges[i])
        indices.remove(ext)
        extracted.append(ext)
        scores.append(rouges[ext])
        if not indices:
            break
        ext = max(indices, key=lambda i: rouges[i])
        indices.append(ext)
        extracted.append(ext)
        scores.append(rouges[ext])
        if not indices:
            break
    return extracted, scores

@curry
def process(split, i):
    data_dir = join(DATA_DIR, split)
    #data_dir = './email_dataset'
    with open(join(data_dir, '{}.json'.format(i))) as f:
        print(join(data_dir, '{}.json'.format(i)))
        data = json.loads(f.read())
    #data = pd.read_csv(r'./email_dataset/Processed_Email_Dataset.csv')
    #data = data.iloc[i]
    tokenize = compose(list, _split_words)
    art_sents = tokenize(data['email_body'])
    abs_sents = tokenize(data['subject'])
    if art_sents and abs_sents: # some data contains empty article/abstract
        extracted, scores = get_extract_label(art_sents, abs_sents)
    else:
        extracted, scores = [], []
    data['extracted'] = extracted
    data['score'] = scores
    with open(join(data_dir, '{}.json'.format(i)), 'w') as f:
        json.dump(data, f, indent=4)
    #data.to_csv(r'./email_dataset/pseudo_labels.csv')

def label_mp(split):
    """ process the data split with multi-processing"""
    start = time()
    print('start processing {} split...'.format(split))
    data_dir = join(DATA_DIR, split)
    n_data = count_data(data_dir)
    print(n_data)
    #n_data = pd.read_csv(r'./email_dataset/Processed_Email_Dataset.csv')
    with mp.Pool() as pool:
        list(pool.imap_unordered(process(split),
                                 list(range(n_data)), chunksize=1024))
    print('finished in {}'.format(timedelta(seconds=time()-start)))

def label(split):
    start = time()
    print('start processing {} split...'.format(split))
    data_dir = join(DATA_DIR, split)
    n_data = count_data(data_dir)
    #n_data = pd.read_csv(r'./email_dataset/Processed_Email_Dataset.csv')
    #df = pd.DataFrame()
    for i in range(n_data):
        print('processing {}/{} ({:.2f}%%)\r'.format(i, n_data, 100*i/n_data),
              end='')
        
        with open(join(data_dir, '{}.json'.format(i))) as f:
            print(data)
            data = json.loads(f.read())
        
        
        #data = n_data.iloc[i]
        tokenize = compose(list, _split_words)
        art_sents = tokenize(data['email_body'])
        abs_sents = tokenize(data['subject'])
        extracted, scores = get_extract_label(art_sents, abs_sents)
        data['extracted'] = extracted
        data['score'] = scores
        with open(join(data_dir, '{}.json'.format(i)), 'w') as f:
            json.dump(data, f, indent=4)
        #df = df.append(data)
    print('finished in {}'.format(timedelta(seconds=time()-start)))
    #df.to_csv('./email_dataset/pseudo_labels.csv')


def main():
    for split in ['val', 'train']:  # no need of extraction label when testing
    #for split in ['train']: 
       label_mp(split)

if __name__ == '__main__':
    main()
