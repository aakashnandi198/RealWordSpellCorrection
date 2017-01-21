from nltk.corpus import brown
from nltk import word_tokenize
import re
#read sentences from brown corpus
sents=brown.sents()

#intialise limits
wrd_limit=10000
limit=0
wrds=0

for i in range(0,len(sents)):
    wrds=wrds+len(sents[i])
    if wrds>wrd_limit:
        limit=i
        break

#opening test file
testfile = open('test.txt', 'w')
#testfile.writelines(["%s\n" % (" ").join(sents[i])  for i in range(0,limit)])
testfile.writelines(["%s\n" % (" ").join(word_tokenize(re.sub('[^a-zA-Z ]+',"",(" ").join(sents[i])))).lower()  for i in range(0,limit)])
testfile.close()

#opening test file
trainfile = open('train.txt', 'w')
#trainfile.writelines(["%s\n" % (" ").join(sents[i])  for i in range(limit,len(sents))])
trainfile.writelines(["%s\n" % (" ").join(word_tokenize(re.sub('[^a-zA-Z ]+',"",(" ").join(sents[i])))).lower()  for i in range(limit,len(sents))])
trainfile.close()

