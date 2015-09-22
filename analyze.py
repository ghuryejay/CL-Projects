import FSM
import util

vocabulary = ['panic', 'picnic', 'ace', 'pack', 'pace', 'traffic', 'lilac', 'ice', 'spruce', 'frolic','kick']
suffixes   = ['', '+ed', '+ing', '+s']

def buildSourceModel(vocabulary, suffixes):
    # we want a language model that accepts anything of the form
    # *   w
    # *   w+s
    fsa = FSM.FSM()
    fsa.setInitialState('start')
    fsa.setFinalState('end')
    
    ### TODO: YOUR CODE HERE

    for word in vocabulary:

        #add edge from start state to first letter in word
        fsa.addEdge('start',word[0],word[0])
        #add edges between letters of remaining word
        word_completed = word[0]

        for i in range(1,len(word)):
            fsa.addEdge(word_completed,word_completed + word[i], word[i])
            word_completed += word[i]

        #add edge to end state from end of the word and to the '+' if suffix exists
        fsa.addEdge(word,'end',None)
        fsa.addEdge(word,'+','+')

    for suffix in suffixes:
        if suffix == '':
            continue
        #add suffixes in similar manner as vocabulary

        fsa.addEdge('start',suffix[0],suffix[0])

        suffix_completed = suffix[0]
        
        for i in range(1,len(suffix)):
            fsa.addEdge(suffix_completed,suffix_completed + suffix[i],suffix[i])
            suffix_completed += suffix[i]

        fsa.addEdge(suffix,'end',None)

    #util.raiseNotDefined()

    return fsa

def buildChannelModel():
    # this should have exactly the same rules as englishMorph.py!
    fst = FSM.FSM(isTransducer=True)
    fst.setInitialState('start')
    fst.setFinalState('end')

    # we can always get from start to end by consuming non-+
    # characters... to implement this, we transition to a safe state,
    # then consume a bunch of stuff
    fst.addEdge('start', 'safe', '.', '.')
    fst.addEdge('safe',  'safe', '.', '.')
    fst.addEdge('safe',  'safe2', '+', None)
    fst.addEdge('safe2', 'safe2', '.', '.')
    fst.addEdge('safe',  'end',  None, None)
    fst.addEdge('safe2',  'end',  None, None)
    
    # implementation of rule 1
    fst.addEdge('start' , 'rule1' , None, None)   # epsilon transition
    fst.addEdge('rule1' , 'rule1' , '.',  '.')    # accept any character and copy it
    fst.addEdge('rule1' , 'rule1b', 'e',  None)   # remove the e
    fst.addEdge('rule1b', 'rule1c', '+',  None)   # remove the +
    fst.addEdge('rule1c', 'rule1d', 'e',  'e')    # copy an e ...
    fst.addEdge('rule1c', 'rule1d', 'i',  'i')    #  ... or an i
    fst.addEdge('rule1d', 'rule1d', '.',  '.')    # and then copy the remainder
    fst.addEdge('rule1d', 'end' , None, None)   # we're done

    # implementation of rule 2
    fst.addEdge('start' , 'rule2' , '.', '.')     # we need to actually consume something
    fst.addEdge('rule2' , 'rule2' , '.', '.')     # accept any character and copy it
    fst.addEdge('rule2' , 'rule2b', 'e', 'e')     # keep the e
    fst.addEdge('rule2b', 'rule2c', '+', None)    # remove the +
    for i in range(ord('a'), ord('z')):
        c = chr(i)
        if c == 'e' or c == 'i':
            continue
        fst.addEdge('rule2c', 'rule2d', c, c)     # keep anything except e or i
    fst.addEdge('rule2d', 'rule2d', '.', '.')     # keep the rest
    fst.addEdge('rule2d', 'end' , None, None)   # we're done

    # implementation of rule 3
    ### TODO: YOUR CODE HERE
     # implementation of rule 3
    fst.addEdge('start', 'rule3', None, None)   # epsilon transition
    fst.addEdge('rule3', 'rule3', '.', '.')     # accept any character and copy it
    fst.addEdge('rule3', 'rule3a', 'c', 'c')    # Found c 
    fst.addEdge('rule3a', 'rule3b', '+', 'k')   # Found a k after c, replace it by +
    fst.addEdge('rule3b', 'rule3b', '.', '.')   # consume and print rest of word

    fst.addEdge('rule3b', 'end', None, None)


    #util.raiseNotDefined()

    return fst

def simpleTest():
    fsa = buildSourceModel(vocabulary, suffixes)
    fst = buildChannelModel()

    print "==== Trying source model on strings 'ace+ed' ===="
    output = FSM.runFST([fsa], ["ace+ed"])
    print "==== Result: ", str(output), " ===="


    print "==== Trying source model on strings 'panic+ing' ===="
    output = FSM.runFST([fsa], ["panic+ing"])
    print "==== Result: ", str(output), " ===="
    
    print "==== Generating random paths for 'aced', using only channel model ===="
    output = FSM.runFST([fst], ["aced"], maxNumPaths=10, randomPaths=True)
    print "==== Result: ", str(output), " ===="

    print "==== Disambiguating a few phrases: aced, panicked, paniced, sprucing ===="
    output = FSM.runFST([fsa,fst], ["aced", "paniced", "panicked", "sprucing","kicks"])
    print "==== Result: ", str(output), " ===="

def main():
    simpleTest()

if __name__ == '__main__':
    main()

    
