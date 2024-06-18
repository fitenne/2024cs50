import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

# S -> N V
NONTERMINALS = """
S -> Sub VP | Sub VP Conj S2
S2 -> VP | VP Conj S2 | Sub VP | Sub VP Conj S2
Sub -> Det AdjN | AdjN
AdjN -> Adjs N | N
Adjs -> Adjs Adj | Adj
VP -> VPClu Sup | VPClu
VPClu -> MV Obj | MV Obj Adv | MV
MV -> Adv V | V Adv | V
Obj -> P Sub | Sub
Sup -> SupT | SupT Sup
SupT -> Det AdjN | P Det AdjN | P AdjN
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence: str):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    l = sentence.lower()
    t = nltk.word_tokenize(l)
    f = filter(lambda s: sum([
        1 if c.isalpha() else 0 for c in s
    ]) != 0, t)
    return list(f)


def np_chunk(tree: nltk.Tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    chunks = []
    def n_np(subtree: nltk.ParentedTree) -> int:
        child = [ n for n in subtree.subtrees() if n.parent() is subtree ]

        n = sum([
            n_np(s) for s in child
        ])
        n += 1 if subtree.label() == 'NP' else 0

        if subtree.label() == 'NP' and n == 1:
            chunks.append(subtree)

        return n

    n_np(nltk.ParentedTree.fromstring(tree.pformat()))
    return chunks


if __name__ == "__main__":
    main()
