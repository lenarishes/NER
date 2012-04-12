import json, sys
import base64
import re
from Datum import Datum

class FeatureFactory:
    """
    Add any necessary initialization steps for your features here
    Using this constructor is optional. Depending on your
    features, you may not need to intialize anything.
    """
    def __init__(self):
        self.Articles = ['a', 'the']
        self.Preps = ['in', 'at', 'on']
        self.Abr_Titles = ['mrs', 'mr', 'ms', 'prof', 'dr', 'gen', 'rep', 'sen', 'st']
        self.Speak = ['said', 'told']
        self.Titles = []
        self.Names = []
        for line in open('titles.txt', 'r'):
            self.Titles.append(line.split()[0].lower())
        for line in open('names.txt', 'r'):
            self.Names.append(line.split()[0].lower())



    """
    Words is a list of the words in the entire corpus, previousLabel is the label
    for position-1 (or O if it's the start of a new sentence), and position
    is the word you are adding features for. PreviousLabel must be the
    only label that is visible to this method. 
    """

    def computeFeatures(self, words, previousLabel, position):
        features = []
        currentWord = words[position]
        
        """ Baseline Features """
        features.append("word=" + currentWord)
        features.append("prevLabel=" + previousLabel)
        features.append("word=" + currentWord + ", prevLabel=" + previousLabel)
        # Uppercase
        if currentWord[0].isupper():
            if currentWord.isupper():
            # pattern X.
                if len(currentWord) == 2 and currentWord[-1] == '.':
            		    features.append("word=Initial")
            		  # sent in CAP or name in CAP?
                features.append("case=Allcap")
            else:
                features.append("case=Title")
                # T.O'Gorman
                if re.search(r"O\'[A-Z]", currentWord):
                    features.append("case=Irish")
                # prev = name + Uppercase
                if previousLabel == 'PERSON':
                    features.append("case=LastName")
                # Doesn't work!! Why?? X said
                if position < len(words) - 1 and words[position + 1].lower() == "'s":
                    features.append("next=Verb_of_Saying")
        # lowercase
        elif currentWord.islower():
            features.append("case=lower")
        # camelcase
        # word from Names
        if currentWord.lower() in self.Names:
             features.append("word=in_names_list")   
        """Judging by the class of previous word"""
        if position > 0:
            prevWord = words[position - 1].lower()
            if prevWord in self.Articles:
                features.append("prev=Article")
            if prevWord in self.Preps:
                features.append("prev=Location prep")
            if prevWord in self.Abr_Titles or prevWord[:-1] in self.Abr_Titles:
                # prev = title (Mr., Ms.)
                features.append("prev=Abbreviated Title")
            if prevWord in self.Titles:
                # prev = title (President, Lady)
                features.append("prev=Title")
        """Search patterns after the word"""
        start = position
        end = position + 6
        context = ' '.join(words[start:end])
        # pattern Name [Last name] ( country )
        if re.match(r'([A-Z]\w+ ){1,2}\( [A-Z][a-z]+ \)', context):
            features.append("next=Country")
        # pattern Name [Last name] ( 13th )
        if re.match(r'([A-Z]\w+ ){1,2}\( [0-9]+(th|st) \)', context):
            features.append("next=Ranked")
        # next word (skip comma) whose, who ...
        if re.match(r'[A-Z]\w+ \, who(se)?', context):
            features.append("next=Who")
        # ? use NLTK postagger?          
        # name? + conjunction
        if re.match(r'([A-Z]\w+ ){1,2}(\,|and|with) [A-Z]\w+', context):
            features.append("next=Homos")
        # 's
        #if re.match(r"[A-Z]\w+ \'s ", context):
        #    features.append("next=Possesive")
        # X said
        #if re.match(r'[A-Z]\w+ (said|told)', context):
        #    features.append("next=Verb_of_Saying")
        # prev word ending in 'an (nationality)
        # XX-year-old
	"""
        Warning: If you encounter "line search failure" error when
        running the program, considering putting the baseline features
	back. It occurs when the features are too sparse. Once you have
        added enough features, take out the features that you don't need. 
	"""


	""" TODO: Add your features here """

        return features

    """ Do not modify this method """
    def readData(self, filename):
        data = [] 
        
        for line in open(filename, 'r'):
            line_split = line.split()
            # remove emtpy lines
            if len(line_split) < 2:
                continue
            word = line_split[0]
            label = line_split[1]

            datum = Datum(word, label)
            data.append(datum)

        return data

    """ Do not modify this method """
    def readTestData(self, ch_aux):
        data = [] 
        
        for line in ch_aux.splitlines():
            line_split = line.split()
            # remove emtpy lines
            if len(line_split) < 2:
                continue
            word = line_split[0]
            label = line_split[1]

            datum = Datum(word, label)
            data.append(datum)

        return data


    """ Do not modify this method """
    def setFeaturesTrain(self, data):
        newData = []
        words = []

        for datum in data:
            words.append(datum.word)

        ## This is so that the feature factory code doesn't
        ## accidentally use the true label info
        previousLabel = "O"
        for i in range(0, len(data)):
            datum = data[i]

            newDatum = Datum(datum.word, datum.label)
            newDatum.features = self.computeFeatures(words, previousLabel, i)
            newDatum.previousLabel = previousLabel
            newData.append(newDatum)

            previousLabel = datum.label

        return newData

    """
    Compute the features for all possible previous labels
    for Viterbi algorithm. Do not modify this method
    """
    def setFeaturesTest(self, data):
        newData = []
        words = []
        labels = []
        labelIndex = {}

        for datum in data:
            words.append(datum.word)
            if not labelIndex.has_key(datum.label):
                labelIndex[datum.label] = len(labels)
                labels.append(datum.label)
        
        ## This is so that the feature factory code doesn't
        ## accidentally use the true label info
        for i in range(0, len(data)):
            datum = data[i]

            if i == 0:
                previousLabel = "O"
                datum.features = self.computeFeatures(words, previousLabel, i)

                newDatum = Datum(datum.word, datum.label)
                newDatum.features = self.computeFeatures(words, previousLabel, i)
                newDatum.previousLabel = previousLabel
                newData.append(newDatum)
            else:
                for previousLabel in labels:
                    datum.features = self.computeFeatures(words, previousLabel, i)

                    newDatum = Datum(datum.word, datum.label)
                    newDatum.features = self.computeFeatures(words, previousLabel, i)
                    newDatum.previousLabel = previousLabel
                    newData.append(newDatum)

        return newData

    """
    write words, labels, and features into a json file
    Do not modify this method
    """
    def writeData(self, data, filename):
        outFile = open(filename + '.json', 'w')
        for i in range(0, len(data)):
            datum = data[i]
            jsonObj = {}
            jsonObj['_label'] = datum.label
            jsonObj['_word']= base64.b64encode(datum.word)
            jsonObj['_prevLabel'] = datum.previousLabel

            featureObj = {}
            features = datum.features
            for j in range(0, len(features)):
                feature = features[j]
                featureObj['_'+feature] = feature
            jsonObj['_features'] = featureObj
            
            outFile.write(json.dumps(jsonObj) + '\n')
            
        outFile.close()

