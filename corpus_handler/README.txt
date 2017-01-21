brown_split.py : Splits the Brown corpus into training set(train.txt) and a testset(test.txt).
generate_testset.py : Generates the T20,T62 and MAL testsets on the testset reserved from brown corpus (test.txt)
lang_model.sh :Generates the language model containing n-gram probabilities in log(base-10) terms.

Order of execution
brown_split.py -> lang_model.sh -> generate_testset.py

