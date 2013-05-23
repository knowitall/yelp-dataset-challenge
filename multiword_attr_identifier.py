import json
import os
from collections import Counter
from util import *

MAX_MULTIWORD_ATTRS = 250
MIN_MULTIWORD_ATTR_COUNT = 200

def identify_multiword_attrs():
  """Identifies bigrams that commonly are collocated according to their
  symmetric conditional probability. Since compound-nouns are automatically
  treated as multi-word attributes in the pre-parsing step, this is only done
  for adjective-noun sequences"""
  word_counts = Counter()
  bigram_counts = Counter()

  files = os.listdir('./data/tagged')
  ll = LoopLogger(2000, len(files), True)
  for filename in files:
    ll.step()
    for sentence in open('./data/tagged/' + filename):
      last_token = "<S>";
      for token in sentence.lower().split(' '):
        word_counts[token] += 1
        if last_token != "<S>":
          bigram_counts[(last_token, token)] += 1
        last_token = token

  scp = {}
  for (a, b) in bigram_counts:
    if bigram_counts[(a, b)] > MIN_MULTIWORD_ATTR_COUNT \
      and len(b.rsplit('/', 1)) > 1 and len(a.rsplit('/', 1)) > 1 \
      and 'nn' in b.rsplit('/', 1)[1] and 'jj' in a.rsplit('/', 1)[1]:
      scp[(a, b)] = float(bigram_counts[(a, b)] ** 2) \
        / (word_counts[a] * word_counts[b])

  best = sorted(scp.keys(), key=lambda bigram: scp[bigram],
                reverse=True)[:MAX_MULTIWORD_ATTRS]

  write_json({"multiword_attributes": best},
             './data/multiword_attributes.json')

if __name__ == '__main__':
  identify_multiword_attrs()
