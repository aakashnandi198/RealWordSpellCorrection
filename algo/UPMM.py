# Credits to Peter Norvig's spell.py base code which can be found at http://norvig.com/spell-correct.html
# Name : Aakash Nandi
# McGill ID:260741007
import re
import nltk
import math
from collections import Counter
from nltk.tokenize import sent_tokenize
from nltk.util import ngrams


# Declaration of Global Variables
# Typist's confidence level
# these values get rewritten in function calls
alpha = 0.9
beta = 0

# vocabulary list
vocab = []

# unigram
unigram={}

# bigram
bigram={}

# trigram
trigram={}

#Backoff weights for unigram
bo_wt_1={}

#Backoff weights for bigram
bo_wt_2={}

# Load vocabulary into a list
def loadvocab(filename):
    vocabfile = open(filename, 'r')
    for line in vocabfile:
        if line[0] != '#' or line[1] != '#':
            if re.match(r'\w+',line):
                vocab.append(line.rstrip())
    vocabfile.close()
    return

#call the funtion to initialize vocab
loadvocab("../corpus_handler/train.vocab")

# Load N-gram into unigram dictionary
def loadngram(filename,n):
    ngramfile = open(filename)
    flag=0
    #read till you find the ngram tag
    for line in ngramfile:
        if n==1:
            if flag==2:
                if line == "\n":
                    break
                unigram[line.rstrip().split(" ")[1].split("\t")[0]]=float(line.rstrip().split(" ")[0])
                bo_wt_1[line.rstrip().split(" ")[1].split("\t")[0]]=float(line.rstrip().split(" ")[1].split("\t")[1])
            if line.rstrip() == "\\1-grams:":
                flag+=1
        if n==2:
            if flag==2:
                if line == "\n":
                    break
                bigram[(line.rstrip().split(" ")[1],line.rstrip().split(" ")[2])]=float(line.rstrip().split(" ")[0])
                bo_wt_2[(line.rstrip().split(" ")[1],line.rstrip().split(" ")[2])]=float(line.rstrip().split(" ")[3])
            if line.rstrip() == "\\2-grams:":
                flag+=1
        if n==3:
            if flag==2:
                if line == "\n":
                    break
                trigram[(line.rstrip().split(" ")[1],line.rstrip().split(" ")[2],line.rstrip().split(" ")[3])]=float(line.rstrip().split(" ")[0])
            if line.rstrip() == "\\3-grams:":
                flag+=1

#load unigrams
loadngram("../corpus_handler/train.arpa",1)
#load bigrams
loadngram("../corpus_handler/train.arpa",2)
#load trigrams
loadngram("../corpus_handler/train.arpa",3)

#transform a word not in vocab to <UNK>
def vocabtrans(word):
    if word in vocab:
        return word
    else:
        return "<UNK>"

#get probability of sentence in log base 10
def getsentenceprob(sent):
    prob=0
    for i in range(0,len(sent)-2):
        if trigram.has_key((vocabtrans(sent[i]),vocabtrans(sent[i+1]),vocabtrans(sent[i+2]))):
            prob=prob+trigram[(vocabtrans(sent[i]),vocabtrans(sent[i+1]),vocabtrans(sent[i+2]))]
        elif bigram.has_key((vocabtrans(sent[i]),vocabtrans(sent[i+1]))) and bigram.has_key((vocabtrans(sent[i+1]),vocabtrans(sent[i+2]))):
            prob=prob+bo_wt_2[(vocabtrans(sent[i]),vocabtrans(sent[i+1]))]+bigram[(vocabtrans(sent[i+1]),vocabtrans(sent[i+2]))]
        elif bigram.has_key((vocabtrans(sent[i+1]),vocabtrans(sent[i+2]))):
            prob=prob+bigram[(vocabtrans(sent[i+1]),vocabtrans(sent[i+2]))]
        else:
            prob=prob+unigram[vocabtrans(sent[i+2])]+bo_wt_1[vocabtrans(sent[i+1])]
    return prob

def edits1(word):
    "All edits that are one edit away from `word`."
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

def known(words):
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in vocab)

def candidates(word):
    "Generate possible spelling corrections for word."
    hld=[]
    hld.extend(known(edits1(word)))
    return hld

#compute the probability of changing a particular word
#my research will be done here
def wordchangeprob(orig,updated,confusion_set):
    prob=0
    if len(orig)==len(updated):
        for i in range(0,len(orig)):
            if orig[i]==updated[i]:
                prob=prob+math.log10(alpha)
            else:
                #compute sum of probabilities of bigrams
                prob_sum=0
                for k in confusion_set:
                    if bigram.has_key((vocabtrans(orig[i-1]),vocabtrans(k))):
                        prob_sum=prob_sum+10**bigram[(vocabtrans(orig[i-1]),vocabtrans(k))]
                    else:
                        prob_sum = prob_sum + 10 ** (unigram[vocabtrans(k)]+bo_wt_1[vocabtrans(orig[i-1])])
                #compute fr fraction of probabilities
                if bigram.has_key((vocabtrans(orig[i-1]),vocabtrans(updated[i]))):
                    fr=(10**bigram[(vocabtrans(orig[i-1]),vocabtrans(updated[i]))])/prob_sum
                else:
                    fr = (10 ** (unigram[vocabtrans(updated[i])]+bo_wt_1[vocabtrans(orig[i-1])])) / prob_sum
                prob=prob+math.log10((1-alpha)*fr)
        return prob
    else:
        print "Original and updated sentences differ in length"
        return prob

#get the corrected sentence
def getbestfitsentence(sent):
    maxprob=wordchangeprob(sent,sent,[])+getsentenceprob(sent)
    best_lst=sent[:]
    for i in range(0,len(sent)):
        #print candidates(sent[i])
        confusion_set=candidates(sent[i])
        for j in confusion_set:
            tmp_lst=sent[:]
            tmp_lst[i]=j
            tmp_prob=getsentenceprob(tmp_lst)+wordchangeprob(sent,tmp_lst,confusion_set)
            #print (" ").join(tmp_lst)+" : "+str(tmp_prob)
            if tmp_prob>maxprob:
                maxprob=tmp_prob
                best_lst=tmp_lst[:]

    return best_lst


#working example
#trail1=["I","was","sitting","in","them","bus","going","there",",","to","meet","my","sister"]
#print getbestfitsentence(trail1)

#working example
#trail1=["I","saw","her","whale","she","was","walking","down","the","road","to","buy","grocery"]
#print getbestfitsentence(trail1)

#non - working example
#trail1=["I","am","watching","a","video","one","my","laptop","which","is","connected","to","power","supply"]
#print getbestfitsentence(trail1)

def pointofdifference(a,b):
    cnt=0;
    if len(a)!=len(b):
        print a
        print " len: "+str(len(a))
        print b
        print " len: "+str(len(b))

    for x in range(0,len(a)):
        if a[x]!=b[x]:
            cnt += 1
    return cnt

def printananlysis(testfile,salpha,sbeta):
    global alpha
    alpha = float(salpha)
    global beta
    beta =float(sbeta)
    truth=[]
    truth_v= [line.lstrip().split(" ") for line in open("../corpus_handler/test.txt",'r')]
    #handling a space bug
    for x in truth_v:
        if x[0]!='':
            truth.append(x)

    test = [line.lstrip().split(" ") for line in open(testfile,'r')]

    fp_cor=0
    tp_cor=0
    fn_cor=0
    tn_cor=0

    fp_det = 0
    tp_det = 0
    fn_det = 0
    tn_det = 0

    print "len of truth : "+str(len(truth))
    print "len of test : " + str(len(test))
    for i in range(0,len(truth)):
        print str(i)+"/"+str(len(truth))
        hld_truth = truth[i]
        hld_test = test[i]

        if len(hld_truth)==len(hld_test):
            print "same lengths"
        else:
            print hld_truth
            print hld_test
        #if hld_test[0]=='':
            #del hld_test[0]
        hld_result=getbestfitsentence(test[i])




        if hld_result== hld_truth and hld_test == hld_result:
            tn_cor += 1
            tn_det += 1
        elif hld_result == hld_truth and hld_test != hld_result:
            tp_cor += 1
            tp_det += 1
        elif hld_result != hld_truth and hld_test != hld_result:
            fp_cor += 1
            if pointofdifference(hld_result,hld_truth)==1:
                tp_det += 1
            else:
                fp_det += 1
        elif hld_result != hld_truth and hld_test == hld_result:
            fn_cor += 1
            fn_det += 1
        print " tp_cor:"+str(tp_cor)+" fp_cor:"+str(fp_cor)+" tn_cor:"+str(tn_cor)+" fn_cor:"+str(fn_cor)
        print " tp_det:" + str(tp_det) + " fp_det:" + str(fp_det) + " tn_det:" + str(tn_det) + " fn_det:" + str(fn_det)

    precision_cor=float(tp_cor)/(tp_cor+fp_cor)
    recall_cor=float(tp_cor)/(tp_cor+fn_cor)
    f1_cor=(2*precision_cor*recall_cor)/(precision_cor+recall_cor)

    result=open("UPMM"+testfile.split("/")[-1].split(".")[0]+"_"+str(beta)+".txt",'w+')
    print "Results for aplha = "+str(salpha)+" on "+testfile.split("/")[-1]
    print "For Correction"
    print "Precision : "+str(precision_cor)
    print "Recall : " + str(recall_cor)
    print "F1 : " + str(f1_cor)
    print "-----------------"

    result.write("Results for aplha = " + str(salpha) + " on " + testfile.split("/")[-1]+"\n")
    result.write("For Correction\n")
    result.write("Precision : " + str(precision_cor)+"\n")
    result.write("Recall : " + str(recall_cor)+"\n")
    result.write("F1 : " + str(f1_cor)+"\n")
    result.write("-----------------\n")

    precision_det = float(tp_det) / (tp_det + fp_det)
    recall_det = float(tp_det) / (tp_det + fn_det)
    f1_det = (2 * precision_det * recall_det) / (precision_det + recall_det)

    print "For Detection"
    print "Precision : " + str(precision_det)
    print "Recall : " + str(recall_det)
    print "F1 : " + str(f1_det)
    print "##################################################\n"

    result.write("For Detection\n")
    result.write("Precision : " + str(precision_det)+"\n")
    result.write("Recall : " + str(recall_det)+"\n")
    result.write("F1 : " + str(f1_det)+"\n")
    result.write("##################################################\n")
    result.close()

#beta though passed as an argument , it is not used
print "running for beta 0.05"
printananlysis("../corpus_handler/test20_10.txt",0.9,0.05)

