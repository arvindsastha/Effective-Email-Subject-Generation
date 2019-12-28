Generate Email Subject: Using prior email conversations & user’s style

Preferred Environment:

	* Anaconda for implementation
	* Git for dependency management

Dependencies
	
	* Python 3 (tested on python 3.6)
	* PyTorch 0.4.0 with GPU and CUDA enabled installation (though the code is runnable on CPU, it would be way too slow)
	* Gensim
	* Cytoolz
	* TensorboardX
	* pltrdy/rouge
	* UMAP
	* Perl
	* pyrogue
	* Tensorflow-gpu
	* cuda
	* lib-www-perl
	* xml-perl
	* nltk
	* word_tokenize_corpus
	* sklearn

ARC Setup:
	
	* Login to the ARC cluster
	* Reserve a login node
	* Create a conda environment and install all the dependencies 

Data Set:

	* We need to download the Enron Email Dataset using wget on the ARC cluster
		- wget https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz

	* This is placed at the level of the project directory

Pre Processing data:

	* Navigate to the project directory

	* We need to set the environment variable 
		DATA = path_to_data_directory

	* Pre Process the emails to flush out irrelevant details
		- python Email_Body_Preprocessing.py

Model training:

	* Generate vocabulary, select similar emails and extract stylometry features from the pre-processed emails
		- python make_vocab.py	

	* Pretrain Word2Vec
		- python train_word2vec.py --path=path_to_save_w2v_model

	* Generate extraction labels for RL training 
		- python make_extraction_labels.py

	* Train the abstractor separately
		- python train_abstractor.py --path=path_to_save_abstractor_model --w2v=path_to_w2v_model

	Move the checkpoints to a different directory before running the extractor

	* Train the extractor separately
		- python train_extractor_ml.py --path=path_to_save_extractor_model --w2v=path_to_w2v_model

	Move the checkpoints to a different directory before running the full RL model

	* Train the full RL model
		- python train_full_rl.py --path=path_to_rl_save_model --abs_dir=path_to_load_abstractor_model --ext_dir=path_to_load_extractor_model

Evaluation:
	To evaluate, you will need to download and setup the official ROUGE and METEOR packages.

		- We use pyrouge (pip install pyrouge to install) to make the ROUGE XML files required by the official perl script. You will also need the 	  		  official ROUGE package. Please specify the path to your ROUGE package by setting the environment variable export 		                               ROUGE=path_to_rouge_directory

		- For METEOR, we only need the JAR file meteor-1.5.jar. We need to specify the file by setting the environment variable export 				    	  METEOR=path_to_meteor_jar
	
		- python eval_full_model.py --[rouge/meteor] --decode_dir=[path/to/save/decoded/files]
   	          Note: Meteor score is calculated as fraction by the meteor-1.5.jar, we usually multiply it by 100 to get the percent
