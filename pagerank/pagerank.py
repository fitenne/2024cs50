import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    if len(corpus[page]) == 0:
        return {
            p: 1 / len(corpus)
                for p, _ in corpus.items()
        }
    
    dist_set: dict[str, float] = {
        p: (1-damping_factor) / len(corpus)
            for p, _ in corpus.items()
    }

    for p in corpus[page]:
        dist_set[p] += damping_factor / len(corpus[page])

    # def check():
    #     sum = 0
    #     for _, v in dist_set.items():
    #         sum += v
    #     if sum != 1:
    #         raise f"The values in returned probability distribution should sum to 1 but got {sum}"
    # check()

    return dist_set


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    rank = {
        p: 0
            for p, _ in corpus.items()
    }

    page_names = [ p for p, _ in corpus.items() ]
    page = random.choice(page_names)
    for _ in range(n):
        r = random.random()
        if r < damping_factor:
            t_model = transition_model(corpus, page, damping_factor)
            r = random.random()
            for next, pro in t_model.items():
                if r < pro:
                    page = next
                    rank[next] += 1
                    break
                else:
                    r -= pro
        else:
            page = random.choice(page_names)
            rank[page] += 1

        
    for pg, pro in rank.items():
        rank[pg] = pro / n
    return rank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    corpus: dict[str, set[str]] = corpus.copy()
    for k, v in corpus.items():
        if len(v) == 0:
            corpus[k] = set(corpus.keys())

    link2: dict[str, set[str]] = {
        p: set()
            for p in corpus.keys()
    }
    for u, vs in corpus.items():
        for v in vs:
            assert u not in link2[v]
            link2[v].add(u)

    this_rank = {
        p: 1 / len(corpus)
            for p in corpus.keys()
    }
    while True:
        next_rank: dict[str, float] = {}

        for p in corpus.keys():
            pro = 0.0
            for u in link2[p]:
                if len(corpus[u]) != 0:
                    pro += this_rank[u] / len(corpus[u])
            pro = (1-damping_factor)/len(corpus) + damping_factor * pro
            next_rank[p] = pro

        print(f"next rank: {next_rank}")
        this_rank, next_rank = next_rank, this_rank

        all_le = lambda threshold: all(
            map(
                lambda v: v <= threshold,
                [this_rank[p] - next_rank[p] for p in corpus.keys()],
            )
        )
        if all_le(0.001):
            break

    return this_rank


if __name__ == "__main__":
    main()
