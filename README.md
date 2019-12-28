
# Generate Email Subject: Using prior email conversations & user’s style 

**Problem statement** 
-----
Task of generating email subject line by considering prior email conversations and sender’s style. 
 
**Introduction** 
-----
In the 21st century, it is not uncommon to receive 100s of emails every day. Given the number of overwhelming emails, it is difficult to keep track of past conversations and generate a suitable subject line for an email. An effective subject line becomes essential to better communicate the purpose and the content of the email. For eg., A subject “Mid-Term Papers Graded” would provide more information than a subject “Mid-Term Papers”. This project addresses that problem by taking prior conversations and user’s style of writing emails/subjects into consideration, to generate an effective subject line that is much closer to user’s style. 

> **User focused Hypothesis:** If we include user’s style of writing emails/subjects while generating an email subject line automatically, then the generated subject line will be closer to original subject line that the user would have written. 

> **Method focused Hypothesis:** If we include prior email conversations while generating email subject lines automatically, then the generated subject line will be more effective, and the accuracy, in terms of automatic metrics like F1 scores of ROGUE1, ROGUE2, ROGUE-L, is expected to improve. 

**Workflow** 
-----
We plan to work with [Zhang and Tetreault's](https://www.aclweb.org/anthology/P19-1043/) email subject line generation model and make several enhancements to achieve the goals stated in our hypotheses. The workflow of their model is as described below

* Emails are pre-processed to flush out irrelevant details such as recipient address, previous conversations in the threads etc., 
* The pre-processed emails are fed to a CNN encoder that classifies each sentence in the email body with a positive and negative label using word overlapping
* The sentence selector chooses two positive sentences out of it and forwards it to the abstractor
* The abstractor is implemented with a sequence-sequence encoder decoder along with a copy mechanism that helps it to copy the relevant phrases from the email body to form the subject line
* The generated subject line is passed through a quality estimator which calculates the quality score between the human annotated subject lines (different from original subject line in the data set) and the generated subject lines
* The quality score is fed back as a reward to the sentence selector which then learns using a reinforcement model
 
**Enhancements Proposed**
------
Zhang and Tetreault's model uses only the current email body to generate the subject lines. Extending this model, we plan to design and add two models: 
1. First that analyses prior email conversations and selects relevant sentences for current email in context; 
2. Second that analyses user’s style and fine tunes the generated email subject. 
 
The proposed model to analyse and select sentences will try to  
* build a graph-based structure to capture conversations between the participants
* find the similarity in the email content between current and previous emails using similarity techniques. One method would be to represent the contents of the prior email [in vector space] as a data structure like trees/graphs that can be compared to the current email [in the vector space]
* select 1 or 2 sentences from the previous emails based on the context (using ngrams or bag of words like techniques) and forward it to the abstractor. The abstractor must be modified to handle 3 or 4 sentences [2 from Zhang and Tetreault's sentence selector and 2 from our model] and therefore will have more relevant information/context to generate email subjects. 

The proposed model to analyse and fine tune to user’s style will try to 
* find power relations between participants: who has power over whom. Identifying it, would narrow down the list of words suitable for the task at hand
* record patterns like sentence structure and frequency of user words using Deep Learning employing encoder mechanisms
* replace a word from generated email subject line with a similar word from user’s dictionary
* try to modify the sentence structure with a recorded sentence pattern. This will be done after the abstractor generates a subject line but before feeding it to the quality estimator. This will make the subject appear to be written by the sender thereby increasing the quality 
 
**Example**
------
Email 1: 
> From: Lara </br>
> To: Team members </br></br>
> Email Body: As my last day is Friday, November 30th, I would love to toast the good times and special memories that I have shared with you over the past five years. Please join me for the party at Teala’s (W. Dallas) on Thursday, November 29th, beginning at 5pm. Looking forward to being with you, Lara 
 
Email 2:  
> From: Lara</br>
> To: Team members</br></br> 
> Email Body: Hey guys, Let’s not forget that we have a party tomorrow. Do show up! See you there.

Zhang and Tetreault's model’s result might be `Don’t forget!` as it takes words from only one email at a time (Email 2 in this case).  But from the above emails, we can infer that second email is a follow-up to the first though it is not explicitly mentioned. Our model will try to analyse this similarity in the content and suggest more relevant email subject including the previous emails. Our model’s expected result is `Party tomorrow at Teala’s at 5PM`.
 
**Performace**
-----
Zhang and Tetreault's quality estimator used 1500 email subject lines generated by 500 people with each email being annotated by 3 persons. Their quality estimator compared the generated email subject with human annotated subjects.  Stylometry tests can be used to compare the generated email subject with the original subject as the original subject was written by the actual sender in his/her own style and they had the context. This would help us validate our user hypothesis. Automatic metrics from text summarization and machine translation like F1 scores would help us validate our method hypothesis.

**Environment Used**
-----
* Anaconda for implementation
* Git for dependency management

**Dependencies**
-----
* Python 3 (tested on python 3.6)
* PyTorch 0.4.0
    with GPU and CUDA enabled installation (though the code is runnable on CPU, it would be way too slow)
* Gensim
* Cytoolz
* Tensorflow-gpu

**Contributors**
-----
[Arvind Sastha](https://github.com/arvindsastha/) </br>
[Bhavana](https://github.com/bhavanabalraj/)

**Credits**
----
Zhang and Tetreault's work on email subject line generation
