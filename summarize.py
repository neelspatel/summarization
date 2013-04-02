#!/usr/bin/python

#correct usage is:
#Correct usage is summarize percentilecutoff inputfile.txt commonwords.txt ignoredwords.txt

import nltk.data
from nltk.tokenize import sent_tokenize
import sys
import os
import numpy
import string

#utility functions for printing
def error(string):
	#red and bold: \033[31m\033[1m \033[0m\033[0m
	return "\033[31m\033[1m" + string + "\033[0m\033[0m"

def success(string):
	#green: \033[32m\033[1m \033[0m\033[0m
	return "\033[32m\033[1m" + string + "\033[0m\033[0m"

def bold(string):
	#bold: \033[1m \033[0m
	return "\033[1m" + string + "\033[0m"

#this section is for obtaining user input
#checks to see if the right number of arguments were given
if len(sys.argv) != 6:
	print error("Correct usage is summarize percentilecutoff inputfile.txt commonwords.txt ignoredwords.txt boostedwords")
	exit(1)

textfile = sys.argv[2]
outputfile = textfile[:-4] + "_sorted.txt"
print bold("The output file will be " + outputfile)

#saves percentile
percentile = sys.argv[1]

#loads in the commonwords and ignored words
commonwords = sys.argv[3]
ignoredwords = sys.argv[4]
boostedwords = sys.argv[5]

#checks to seeif the input file is a text file
if textfile[-4:] != '.txt':
	print error("Correct usage is summarize percentilecutoff inputfile.txt commonwords.txt ignoredwords.txt boostedwords")
	print error("You provided " + textfile + " instead of a proper text file.")
	exit(1)	

#opens the file to read it in
infile = open(textfile)

#checks to seeif the commonwords file is a text file
if commonwords[-4:] != '.txt':
	print error("Correct usage is summarize percentilecutoff inputfile.txt commonwords.txt ignoredwords.txt boostedwords")
	print error("You provided " + commonwords + " instead of a proper text file.")
	exit(1)	

#opens the file to read it in
commonfile = open(commonwords)

#checks to seeif the ignoredwords file is a text file
if ignoredwords[-4:] != '.txt':
	print error("Correct usage is summarize percentilecutoff inputfile.txt commonwords.txt ignoredwords.txt boostedwords")
	print error("You provided " + ignoredwords + " instead of a proper text file.")
	exit(1)	

#opens the file to read it in
ignoredfile = open(ignoredwords)

#checks to seeif the boostedwords file is a text file
if boostedwords[-4:] != '.txt':
	print error("Correct usage is summarize percentilecutoff inputfile.txt commonwords.txt ignoredwords.txt boostedwords")
	print error("You provided " + boostedwords + " instead of a proper text file.")
	exit(1)	

#opens the file to read it in
boostedfile = open(boostedwords)

#creates a list to store sentences in, and a dictionary for words, as well as lists for common and ignored words
sentences = []
words = {}
sentences_with_scores = {}
ignored = []
common = []
boosted = {}

#reads in the common and ignored words
print bold("Now reading the list of common words.")

for line in commonfile:
	#adds the word to the common list, making sure they're lowercase
	common.append(line.strip().lower())

commonfile.close()
print "Loaded " + str(len(common)) + " words in the common list"

print bold("Now reading the list of ignored words.")

for line in ignoredfile:
	#adds the word to the ignored list, making sure they're lowercase
	ignored.append(line.strip().lower())

ignoredfile.close()
print "Loaded " + str(len(ignored)) + " words in the ignored list"

print bold("Now reading the list of boosted words.")

linenum = 0
for line in boostedfile:
	#adds the word to the boosted list, making sure they're lowercase
	parts = line.split()
	linenum = linenum + 1

	if len(parts) != 2:
		print error("Sorry, there was an error on line "  + linenum + " of the boosted file.")
		print error(line) + " is not a valid entry."
		exit(1)

	boosted[parts[0].lower()] = parts[1]

boostedfile.close()
print "Loaded " + str(len(boosted)) + " words in the boosted list"

print bold("Now reading each line in the inputfile.")

for line in infile:
	#remove newline char and tokenize the line
	line = line.strip()	
	curr_list = list(sent_tokenize(line))	

	#add current sentence to the overall list
	sentences += curr_list

#uses a list comprehension to filter out the blank strings (or '') from a list
sentences = filter(None, sentences)

print bold("Now parsing each word from the sentences to determine word frequency.")

#creates a list of words and their counts
total_count = 0
unique_count = 0

for sentence in sentences:
	current_words = nltk.tokenize.word_tokenize(sentence)
	
	#for each word, checks if it is in the dictionary (as long as it's not a common or ignored word)
	for word in current_words:
		total_count = total_count + 1
		word = word.lower()
		if not (word in common or word in ignored or word in string.punctuation):	
			unique_count = unique_count + 1	
			if word in words:
				words[word] = words[word] + 1
			else:
				words[word] = 1

#now boosts the frequency of selected boosted words
print bold("Now boosting relevant scores")
for word, boost in boosted.items():
	if word in words:
		words[word] = float(words[word] * boost)

print bold("Now calculating the score of each sentence.")

#now calculates the score of each sentence
for sentence in sentences:
	current_words = nltk.tokenize.word_tokenize(sentence)
	current_score = 0
	num_words = 0

	#for each word, adds the score to this total,
	#as long as it's not common or ignored
	for word in current_words:
		word = word.lower()
		if not (word in common or word in ignored or word in string.punctuation):		
			current_score += words[word]		
			num_words = num_words + 1

	if num_words == 0:
		sentence_score = 0
	else:
		sentence_score = current_score / float(num_words)

	sentences_with_scores[sentence] = sentence_score

print bold("Now calculating the percentile cutoffs.")
#now calculates the relevant metrics for each sentence
values = numpy.array(sentences_with_scores.values())
percentilecutoff = numpy.percentile(values, float(percentile))
print "The percentile cutoff was set by the user at the " + bold(str(percentile)) + "th percentile, which is a score of " + bold(str(percentilecutoff))

#print sentences_with_scores
#print sorted(sentences_with_scores, key = sentences_with_scores.get)
sorted_sentences = list(reversed(sorted(sentences_with_scores, key = sentences_with_scores.get)))
infile.close()

#creates a new directory to write output to
directory_name = textfile[:-4] + "_results/"
os.system("mkdir " + directory_name)

#saves the output as a sorted list
outfile = open(directory_name + outputfile, 'w')
print bold("Writing all sentences to the file " + outputfile + " in order of descending score.")

for sorted_sentence in sorted_sentences:
	outfile.write(str(sentences_with_scores[sorted_sentence]) + "\t" + sorted_sentence + "\n")
outfile.close()

#saves the output as sentences in order of appearance
outputfile = textfile[:-4] + "_summarized.txt"
outfile = open(directory_name + outputfile, 'w')
print bold("Writing only relevant sentences to the file " + outputfile + " in order of appearance.")

#calculates the minimum threshold percentile
summarized_count = 0
for sentence in sentences:
	if sentences_with_scores[sentence] > percentilecutoff:
		outfile.write(sentence + "\n")
		summarized_count = summarized_count + 1
outfile.close()

#saves the list of words and associated frequency counts
outputfile = textfile[:-4] + "_words.txt"
outfile = open(directory_name + outputfile, 'w')
print bold("Writing all words to the file " + outputfile)

for word, score in words.items():
	outfile.write(word + ":" + str(score) + "\n")
outfile.close()

print success("\nCongratulations - your analysis is complete!\n")

#prints out summary of results
print bold("Summary of results:")

print " - There were " + bold(str(len(sorted_sentences))) + " total sentences in the input file."
print " - In the summarized version, there were " + bold(str(summarized_count))+ " sentences."
print " - The sentence scores ranged from " + bold(str(numpy.amin(values))) + " to " + bold(str(numpy.amax(values))) + " with a mean of " + bold(str(numpy.mean(values))) + " and a standard deviation of " + bold(str(numpy.std(values)))
print " - The 10th percentile was " + bold(str(numpy.percentile(values, 10)))
print " - The 50th percentile was " + bold(str(numpy.percentile(values, 50)))
print " - The 90th percentile was " + bold(str(numpy.percentile(values, 90)))
print " - There were " + str(total_count) + " total words, of which " + str(unique_count) + " are not common words"


