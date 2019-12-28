# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 23:22:02 2019

@author: cegbh
"""

import sys
import os
import hashlib
import subprocess
import collections
import pandas as pd
from Similarity_model import SimilarEmail
from corpus import Corpus
import json
import tarfile
import io
import pickle as pkl
import pandas as pd
from nltk import word_tokenize


dm_single_close_quote = '\u2019' # unicode
dm_double_close_quote = '\u201d'
# acceptable ways to end a sentence
END_TOKENS = ['.', '!', '?', '...', "'", "`", '"',
              dm_single_close_quote, dm_double_close_quote, ")"]

tokenized_email_dir = "./email_dataset/preprocessed_data/"
finished_files_dir = "./email_dataset/finished_files"

# These are the number of .story files we expect there to be in cnn_stories_dir
# and dm_stories_dir
num_expected_cnn_stories = 9300

def tokenize_stories(stories_dir, tokenized_stories_dir):
    """Maps a whole directory of .story files to a tokenized version using
       Stanford CoreNLP Tokenizer
    """
    print("Preparing to tokenize {} to {}...".format(stories_dir,
                                                     tokenized_stories_dir))
    stories = os.listdir(stories_dir)
    # make IO list file
    print("Making list of files to tokenize...")
    with open("mapping.txt", "w") as f:
        for s in stories:
            f.write(
                "{} \t {}\n".format(
                    os.path.join(stories_dir, s),
                    os.path.join(tokenized_stories_dir, s)
                )
            )
    command = ['java', 'edu.stanford.nlp.process.PTBTokenizer',
               '-ioFileList', '-preserveLines', 'mapping.txt']
    print("Tokenizing {} files in {} and saving in {}...".format(
        len(stories), stories_dir, tokenized_stories_dir))
    subprocess.call(command)
    print("Stanford CoreNLP Tokenizer has finished.")
    os.remove("mapping.txt")

    # Check that the tokenized stories directory contains the same number of
    # files as the original directory
    num_orig = len(os.listdir(stories_dir))
    num_tokenized = len(os.listdir(tokenized_stories_dir))
    if num_orig != num_tokenized:
        raise Exception(
            "The tokenized stories directory {} contains {} files, but it "
            "should contain the same number as {} (which has {} files). Was"
            " there an error during tokenization?".format(
                tokenized_stories_dir, num_tokenized, stories_dir, num_orig)
        )
    print("Successfully finished tokenizing {} to {}.\n".format(
        stories_dir, tokenized_stories_dir))

def LSA(email):
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
    
    corpus_object = Corpus(news_df['clean_doc'])
    se = SimilarEmail(corpus_object, news_df['clean_doc'])
    similar_text = se.getSimilarEmail(email)
    total_text = email + similar_text + "\n\n\n"

def read_story_file(text_file):
    #with open(text_file, "r") as f:
        # sentences are separated by 2 newlines
        # single newlines might be image captions
        # so will be incomplete sentence
    lines = text_file.split('.')
        #for i, line in enumerate(lines):
        #    lines[i] = line+ "."
    return lines


def hashhex(s):
    """Returns a heximal formated SHA1 hash of the input string."""
    h = hashlib.sha1()
    h.update(s.encode())
    return h.hexdigest()


def fix_missing_period(line):
    """Adds a period to a line that is missing a period"""
    #if "@highlight" in line:
    #    return line
    if line == "":
        return line
    if line[-1] in END_TOKENS:
        return line
    #return line + " ."
    return line


def get_art_abs(story_file):
    """ return as list of sentences"""
    lines = read_story_file(story_file)

    # Lowercase, truncated trailing spaces, and normalize spaces
    lines = [' '.join(line.lower().strip().split()) for line in lines]

    # Put periods on the ends of lines that are missing them (this is a problem
    # in the dataset because many image captions don't end in periods;
    # consequently they end up in the body of the article as run-on sentences)
    lines = [fix_missing_period(line) for line in lines]

    # Separate out article and abstract sentences
    article_lines = []
    #highlights = []
    #next_is_highlight = False
    for idx, line in enumerate(lines):
        if line == "":
            continue # empty line
        #elif line.startswith("@highlight"):
        #    next_is_highlight = True
        #elif next_is_highlight:
        #    highlights.append(line)
        else:
            article_lines.append(line)

    return article_lines


def write_to_tar(indicator, out_file, makevocab=False):
    '''
    """Reads the tokenized .story files corresponding to the urls listed in the
       url_file and writes them to a out_file.
    """
    print("Making bin file for URLs listed in {}...".format(url_file))
    url_list = [line.strip() for line in open(url_file)]
    url_hashes = get_url_hashes(url_list)
    story_fnames = [s+".story" for s in url_hashes]
    num_stories = len(story_fnames)
    '''

    if makevocab:
        vocab_counter = collections.Counter()
    
    email_data = pd.read_csv('./emails_and_subject_val.csv')
    if indicator == "val":
        email_data = email_data[3568:]
    else:
        email_data = email_data[:3567]

    num_stories = len(email_data)
    #print(email_data)
    
    subjects = []
    email_body = []
    file_id = 0
    with tarfile.open(out_file, 'w') as writer:
        for idx in range(num_stories):
            print(idx)
            if idx % 100 == 0:
                print("Writing story {} of {}; {:.2f} percent done".format(
                    idx, num_stories, float(idx)*100.0/float(num_stories)))
            
            '''
            # Look in the tokenized story dirs to find the .story file
            # corresponding to this url
            if os.path.isfile(os.path.join(cnn_tokenized_stories_dir, s)):
                story_file = os.path.join(cnn_tokenized_stories_dir, s)
            elif os.path.isfile(os.path.join(dm_tokenized_stories_dir, s)):
                story_file = os.path.join(dm_tokenized_stories_dir, s)
            else:
                print("Error: Couldn't find tokenized story file {} in either"
                      " tokenized story directories {} and {}. Was there an"
                      " error during tokenization?".format(
                          s, cnn_tokenized_stories_dir,
                          dm_tokenized_stories_dir))
                # Check again if tokenized stories directories contain correct
                # number of files
                print("Checking that the tokenized stories directories {}"
                      " and {} contain correct number of files...".format(
                          cnn_tokenized_stories_dir, dm_tokenized_stories_dir))
                check_num_stories(cnn_tokenized_stories_dir,
                                  num_expected_cnn_stories)
                check_num_stories(dm_tokenized_stories_dir,
                                  num_expected_dm_stories)
                raise Exception(
                    "Tokenized stories directories {} and {}"
                    " contain correct number of files but story"
                    " file {} found in neither.".format(
                        cnn_tokenized_stories_dir,
                        dm_tokenized_stories_dir, s)
                )
            '''

            # Get the strings to write to .bin file
            article = str(email_data.iloc[idx]['Email Body'])
            article_sents = LSA(article_sents)
            article_sents = get_art_abs(article)
 #           fl = 0
 #           copy = []
 #           for i in range(len(article_sents)):
 #               if len(article_sents[i]) >= 5:
 #                    copy.append(article_sents[i])

 #           if len(copy) <= 3:
 #               continue

 #           article_sents = copy

            abstract = str(email_data.iloc[idx]['Subject'])
            abstract_sents = get_art_abs(abstract)
            print(article_sents)
            
            article_sents = [' '.join(word_tokenize(line)) for line in article_sents]
            abstract_sents = [' '.join(word_tokenize(line)) for line in abstract_sents]
                
            copy = []
            for i in range(len(article_sents)):
            #abstract_sents = word_tokenize(abstract_sents)
                if len(article_sents[i].split()) >= 5:
                     copy.append(article_sents[i])
            #abstract_sents = ' '.join(abstract_sents)
            if len(copy) <= 3:
                continue

            print(article_sents)
            article_sents = copy
            
            subjects.append(abstract_sents)
            email_body.append(article_sents)
            # Write to JSON file
            js_example = {}
            js_example['id'] = file_id
            #s.replace('.story', '')
            js_example['email_body'] = article_sents
            js_example['subject'] = abstract_sents
            js_serialized = json.dumps(js_example, indent=4).encode()
            save_file = io.BytesIO(js_serialized)
            tar_info = tarfile.TarInfo('{}/{}.json'.format(
                os.path.basename(out_file).replace('.tar', ''), file_id))
            tar_info.size = len(js_serialized)
            writer.addfile(tar_info, save_file)

            # Write the vocab to file, if applicable
            if makevocab:
                art_tokens = ' '.join(article_sents).split()
                abs_tokens = ' '.join(abstract_sents).split()
                print(art_tokens)
                tokens = art_tokens + abs_tokens
                tokens = [t.strip() for t in tokens] # strip
                tokens = [t for t in tokens if t != ""] # remove empty
                vocab_counter.update(tokens)
            file_id = file_id + 1
    print("Finished writing file {}\n".format(out_file))

    # write vocab to file
    if makevocab:
        print("Writing vocab file...")
        with open(os.path.join(finished_files_dir, "vocab_cnt.pkl"),
                  'wb') as vocab_file:
            pkl.dump(vocab_counter, vocab_file)
        print("Finished writing vocab file")
    
    print(len(email_data))
    
    df = pd.DataFrame()
    df['Subject'] = subjects
    df['Email_Body'] = email_body
    df.to_csv('./email_dataset/Processed_Email_Dataset.csv', index=False)

def check_num_stories(stories_dir, num_expected):
    num_stories = len(os.listdir(stories_dir))
    if num_stories != num_expected:
        raise Exception(
            "stories directory {} contains {} files"
            " but should contain {}".format(
                stories_dir, num_stories, num_expected)
        )


if __name__ == '__main__':
    if len(sys.argv) != 1:
        print("USAGE: python make_datafiles.py"
              " <email_stories_dir>")
        sys.exit()
    #cnn_stories_dir = sys.argv[1]
    
    # Check the stories directories contain the correct number of .story files
    #check_num_stories(cnn_stories_dir, num_expected_cnn_stories)
    #check_num_stories(dm_stories_dir, num_expected_dm_stories)

    # Create some new directories
    #if not os.path.exists(tokenized_email_dir):
    #    os.makedirs(tokenized_email_dir)
    #if not os.path.exists(dm_tokenized_stories_dir):
    #    os.makedirs(dm_tokenized_stories_dir)
    #if not os.path.exists(finished_files_dir):
    #    os.makedirs(finished_files_dir)

    # Run stanford tokenizer on both stories dirs,
    # outputting to tokenized stories directories
    #data = pd.read_csv('./email_dataset/Sentence_And_Subject_Emails.csv')
    
    #for i in range(len(data)):
    #    command = ['java', 'edu.stanford.nlp.process.PTBTokenizer',
    #               '-preserveLines', data.iloc[i]['Email_Body']]
    #    print("Tokenizing {} files in {} and saving in {}...".format(
    #            len(stories), stories_dir, tokenized_stories_dir))
    #    subprocess.call(command)
    
    #tokenize_stories(cnn_stories_dir, tokenized_email_dir)
    #tokenize_stories(dm_stories_dir, dm_tokenized_stories_dir)

    # Read the tokenized stories, do a little postprocessing
    # then write to bin files
    #write_to_tar(os.path.join(finished_files_dir, "test.tar"))
    write_to_tar("val", os.path.join(finished_files_dir, "val.tar"))
    
    write_to_tar("train", os.path.join(finished_files_dir, "train.tar"),
                 makevocab=True)
    file = pkl.load(open('./email_dataset/finished_files/vocab_cnt.pkl','rb'))
    print(file)
