from FSM import *
import FSM
from util import *
import util

def readData(filename):
    h = open(filename, 'r')
    words = []
    segmentations = []
    for l in h.readlines():
        a = l.split()
        if len(a) == 1:
            words.append(a[0])
            segmentations.append(None)
        elif len(a) == 2:
            words.append(a[0])
            segmentations.append(a[1])
    return (words, segmentations)

def evaluate(truth, hypothesis):
    I = 0
    T = 0
    H = 0
    for n in range(len(truth)):
        if truth[n] is None: continue
        t = truth[n].split('+')
        allT = {}
        cumSum = 0
        for ti in t:
            cumSum = cumSum + len(ti)
            allT[cumSum] = 1

        h = hypothesis[n].split('+')
        allH = {}
        cumSum = 0
        for hi in h:
            cumSum = cumSum + len(hi)
            allH[cumSum] = 1

        T = T + len(allT) - 1
        H = H + len(allH) - 1
        for i in allT.iterkeys():
            if allH.has_key(i):
                I = I + 1
        I = I - 1
        
    Pre = 1.0
    Rec = 0.0
    Fsc = 0.0
    if I > 0:
        Pre = float(I) / H
        Rec = float(I) / T
        Fsc = 2 * Pre * Rec / (Pre + Rec)
    return (Pre, Rec, Fsc)

def stupidChannelModel(words, segmentations):
    # figure out the character vocabulary
    vocab = Counter()
    for w in words:
        for c in w:
            vocab[c] = vocab[c] + 1

    # build the FST    
    fst = FSM.FSM(isTransducer=True, isProbabilistic=True)
    fst.setInitialState('s')
    fst.setFinalState('s')
    for w in words:
        for c in w:
            fst.addEdge('s', 's', c, c, prob=1.0)    # copy the character
    fst.addEdge('s', 's', '+', None, prob=0.1)       # add a random '+'
    return fst

def stupidSourceModel(segmentations):
    # figure out the character vocabulary
    vocab = Counter()
    for s in segmentations:
        for c in s:
            vocab[c] = vocab[c] + 1
    # convert to probabilities
    vocab.normalize()

    # build the FSA
    fsa = FSM.FSM(isProbabilistic=True)
    fsa.setInitialState('s')
    fsa.setFinalState('s')
    for c,v in vocab.iteritems():
        fsa.addEdge('s', 's', c, prob=v)
    return fsa

def bigramSourceModel(segmentations):
    # compute all bigrams
    lm = {}
    vocab = {}
    vocab['end'] = 1
    for s in segmentations:
        prev = 'start'
        for c in s:
            if not lm.has_key(prev): lm[prev] = Counter()
            lm[prev][c] = lm[prev][c] + 1
            prev = c
            vocab[c] = 1
        if not lm.has_key(prev): lm[prev] = Counter()
        lm[prev]['end'] = lm[prev]['end'] + 1

    # smooth and normalize
    for prev in lm.iterkeys():
        for c in vocab.iterkeys():
            lm[prev][c] = lm[prev][c] + 0.5   # add 0.5 smoothing
        lm[prev].normalize()

    # convert to a FSA
    fsa = FSM.FSM(isProbabilistic=True)
    fsa.setInitialState('start')
    fsa.setFinalState('end')
    ### TODO: YOUR CODE HERE
    #adding edge from start state to first characters of words
    for c in lm['start']:
        fsa.addEdge('start',c,c,prob=lm['start'][c])
    #add edges between remaining characters of each word
    for key in lm.keys():
        if key != 'start':
            for c in lm[key]:
                #for edge to end state
                if c == 'end':
                    fsa.addEdge(key,c,None,prob=lm[key][c])
                #for edge to next character
                else:
                    fsa.addEdge(key,c,c,prob=lm[key][c])

    #util.raiseNotDefined()
    return fsa

def buildSegmentChannelModel(words, segmentations):
    fst = FSM.FSM(isTransducer=True, isProbabilistic=True)
    fst.setInitialState('start')
    fst.setFinalState('end')
    ### TODO: YOUR CODE HERE
    #util.raiseNotDefined()
    characters = {}
    segments_processed = {}
    for segments in segmentations:
        segments = segments.split('+')
        for segment in segments:
            if segment not in segments_processed:
                segments_processed[segment] = 1
                #edge from start to first character
                fst.addEdge('start',segment[0],segment[0],segment[0],prob=1)
                processed_seg = segment[0]
                remaining_seg = segment[1:]
                for s in remaining_seg:
                    if s not in characters:
                        characters[s] = 1
                    fst.addEdge(processed_seg,processed_seg + s, s, s,prob=1)
                    processed_seg += s

                #add edge to end state
                fst.addEdge(segment,'end',None,None,prob=1)
                #add edge to start state for processing part after +
                fst.addEdge(segment,'start','+',None,prob=1)

    #add edges from start to unseen characters for smoothing
    for char in characters:
        fst.addEdge('start','start',char,char,prob=0.1)

    fst.addEdge('start','start','+',None,prob=0.1)

    '''
    fst.addEdge('start', 'intermediate', None, None, prob=0.1)
    fst.addEdge('intermediate', 'start', '+', None, prob=0.1)
    fst.addEdge('intermediate', 'end', None, None, prob=0.1)
    '''

    return fst


def fancySourceModel(segmentations):
    # compute all tri-grams
    lm = {}
    vocab = {}
    vocab['start'] = 1
    vocab['end'] = 1

    for s in segmentations:
        prev0 = 'start'
        prev1 = 'start'
        for c in s:
            if not lm.has_key(prev0): 
                lm[prev0] = {}
            if not lm[prev0].has_key(prev1): 
                lm[prev0][prev1] = Counter()
            lm[prev0][prev1][c] = lm[prev0][prev1][c] + 1
            prev0 = prev1
            prev1 = c
            vocab[c] = 1
        if not lm.has_key(prev0): 
            lm[prev0] = {}
        if not lm[prev0].has_key(prev1): 
            lm[prev0][prev1] = Counter()
        lm[prev0][prev1]['end'] = lm[prev0][prev1]['end'] + 1

    # smooth and normalize
    for prev0 in vocab.iterkeys():
        if prev0 not in lm:
            lm[prev0] = {}
        for prev1 in vocab.iterkeys():
            if prev1 not in lm[prev0]:
                lm[prev0][prev1] = Counter()
            for c in vocab.iterkeys():
                lm[prev0][prev1][c] = lm[prev0][prev1][c] + 0.5   # add 0.5 smoothing
            lm[prev0][prev1].normalize()

    # convert to a FSA
    fsa = FSM.FSM(isProbabilistic=True)
    fsa.setInitialState('start')
    fsa.setFinalState('end')
    ### TODO: YOUR CODE HERE
    #adding edge from start state to first characters of words
    for first_char in vocab.iterkeys():

        fsa.addEdge('start', first_char, first_char, prob=lm['start']['start'][first_char])
        for second_char in vocab.iterkeys():
            
            fsa.addEdge(first_char, first_char + second_char, second_char, prob=lm['start'][first_char][second_char])
    
    
    for key0 in vocab:
        if key0 != 'start':
            for key1 in vocab:
                if key1 != 'start':
                    for curr in vocab:

                        if curr != 'end':
                            fsa.addEdge(key0+key1,key1+curr,curr,prob=lm[key0][key1][curr])
                        else:
                            fsa.addEdge(key0+key1,'end',None,prob=lm[key0][key1][curr])

    #util.raiseNotDefined()
    return fsa


def fancyChannelModel(words, segmentations):
    return buildSegmentChannelModel(words, segmentations)

    
def runTest(trainFile='bengali.train', devFile='bengali.dev', channel=stupidChannelModel, source=stupidSourceModel, skipTraining=False):
    (words, segs) = readData(trainFile)
    (wordsDev, segsDev) = readData(devFile)
    fst = channel(words, segs)
    fsa = source(segs)

    preTrainOutput = runFST([fsa, fst], wordsDev, quiet=True)
    for i in range(len(preTrainOutput)):
        if len(preTrainOutput[i]) == 0: preTrainOutput[i] = words[i]
        else:                           preTrainOutput[i] = preTrainOutput[i][0]
    preTrainEval   = evaluate(segsDev, preTrainOutput)
    print 'before training, P/R/F = ', str(preTrainEval)

    if skipTraining:
        return preTrainOutput
    
    fst.trainFST(words, segs)

    postTrainOutput = runFST([fsa, fst], wordsDev, quiet=True)
    for i in range(len(postTrainOutput)):
        if len(postTrainOutput[i]) == 0: postTrainOutput[i] = words[i]
        else:                            postTrainOutput[i] = postTrainOutput[i][0]
    postTrainEval   = evaluate(segsDev, postTrainOutput)
    print 'after  training, P/R/F = ', str(postTrainEval)
    
    return postTrainOutput

def saveOutput(filename, output):
    h = open(filename, 'w')
    for o in output:
        h.write(o)
        h.write('\n')
    h.close()

def main():
    output = runTest(devFile='bengali.test',source=fancySourceModel)
    saveOutput('bengali.test.predictions', output)
if __name__ == '__main__':
    main()
    
