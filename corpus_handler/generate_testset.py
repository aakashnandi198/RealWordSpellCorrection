import re
import random
from nltk.corpus import wordnet as wn
from subprocess import Popen,PIPE


# vocabulary list
vocab20 = []
vocab62= []
#wordnet nons
nouns = {x.name().split('.', 1)[0] for x in wn.all_synsets('n')}
ispell_loc="/usr/bin/ispell"

# Load vocabulary into a list
def loadvocab(filename):
    vocab=[]
    vocabfile = open(filename, 'r')
    for line in vocabfile:
        if line[0] != '#' or line[1] != '#':
            if re.match(r'\w+',line):
                vocab.append(line.lower().rstrip())
    vocabfile.close()
    return vocab

#call the funtion to initialize vocab
vocab20=loadvocab("/home/aakash/Desktop/nlp_project/corpus_handler/train.vocab",)
vocab62=loadvocab("/home/aakash/Desktop/nlp_project/corpus_handler/train_62.vocab",)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def ispellpresent(word):
    p=Popen([ispell_loc,'-a','-S'],stdin=PIPE,stdout=PIPE)
    captured = p.communicate(word)
    if captured[0].split('\n')[1].startswith('&'):
        return False
    else:
        return True

def known(words,type):
    "The subset of `words` that appear in the dictionary of WORDS."
    if type==20:
        return [w for w in words if w in vocab20]
    elif type==62:
        return [w for w in words if w in vocab62]
    elif type==0:
        return [w for w in words if ispellpresent(w)]

def candidates(word,type):
    "Generate possible spelling corrections for word."
    hld = []
    hld.extend(known(edits1(word),type))
    return hld

def generatetestset(t,error_in):
    test=open("test.txt",'r')
    if t==20:
        test_r=open("test20_"+str(error_in)+".txt",'w+')
    elif t==62:
        test_r = open("test62_"+str(error_in)+".txt", 'w+')
    elif t==0:
        test_r = open("testmal_"+str(error_in)+".txt",'w+')

    wrds=0
    cnt=0
    chunk=[]
    for line in test:
        #print "running for line "+str(cnt)
        cnt=cnt+1
        wrds=wrds+len(line.lstrip().split(" "))
        chunk.extend(line.lstrip().split(" "))

        if wrds>error_in:
            #perform replacement activity
            #write to test
            k=random.randint(0,error_in-1)
            flg=0

            #looking for a word that is in vocab20 list
            if t==20:
                while chunk[k] not in vocab20:
                    if k==0 and flg==1:
                        break
                    if k==0:
                        flg=1
                    k=(k+1)%len(chunk)
                if k==0 and flg==1:
                    continue
                else:
                    c_lst=candidates(chunk[k],20)

            #looking for a word in vocab62 with replacements in vocab20
            elif t==62:
                while chunk[k] not in vocab62:
                    if k==0 and flg==1:
                        break
                    if k==0:
                        flg=1
                    k=(k+1)%len(chunk)
                if k==0 and flg==1:
                    continue
                else:
                    c_lst=candidates(chunk[k],62)

            #looking for a word which is noun in wordnet with replacement in vocab20
            elif t==0:
                while chunk[k] not in nouns or len(chunk[k])<=1:
                    if k==0 and flg==1:
                        break
                    if k==0:
                        flg=1
                    k=(k+1)%len(chunk)
                if k==0 and flg==1:
                    continue
                else:
                    c_lst=candidates(chunk[k],0)

            max_index=len(c_lst)
            if max_index!=0:
                #print "max_index : "+str(max_index)
                j=random.randint(0,max_index-1)
                flg=0
                while c_lst[j].lower()==chunk[k].lower():
                    if j==0 and flg==1:
                        break
                    if j==0:
                        flg=1
                    j=(j+1)%max_index
                if k == 0 and flg == 1:
                    continue
                #print "range "+str(max_index)+": j "+str(j)

                print "changing "+chunk[k]+" "+c_lst[j]
                chunk[k]=c_lst[j]


            test_r.write((" ").join(chunk))
            print (" ").join(chunk)
            wrds=0
            chunk=[]

    test.close()
    test_r.close()


generatetestset(20,10)
print "###################### t20_10 Done ##############################"

generatetestset(62,10)
print "###################### t62_10 Done ##############################"

generatetestset(0,10)
print "###################### mal_10 Done ##############################"
