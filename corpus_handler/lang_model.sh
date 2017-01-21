text2wfreq < train.txt > train.wfreq
wfreq2vocab -top 20000 < train.wfreq > train.vocab
wfreq2vocab -top 62000 < train.wfreq > train_62.vocab
text2idngram -vocab train.vocab -temp /home/aakash/Desktop/nlp_project/corpus_handler -write_ascii < train.txt > train.idngram 
idngram2lm -idngram train.idngram -vocab train.vocab -arpa train.arpa -good_turing -ascii_input 

