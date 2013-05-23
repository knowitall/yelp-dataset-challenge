import os
import json
from operator import itemgetter
from util import *

CHUNK_SIZE = 20000

def combine_multi_words(sentence, multiword_attrs):
  """Groups noun compounds and bigrams identified as multi-word attributes
  together to be treated as a single unit by the parser"""
  token_tag_pairs = []
  last_tag = lastToken = None
  last_TAT = ''
  for TAT in sentence.split(' '):
    split_TAT = TAT.rsplit('/', 1)
    if len(split_TAT) < 2:
      last_tag = lastToken = None
      continue
    token, tag = split_TAT

    if token == '-LRB-':
      token = '('
    elif token == '-RRB-':
      token = ')'

    if tag and last_tag and  \
        ((tag.find('NN') != -1 and last_tag.find('NN') != -1) \
        or (last_TAT.lower(), TAT.lower()) in multiword_attrs):
      token_tag_pairs[-1] = (token_tag_pairs[-1][0] + '#' + token, 'NN')
    else:
      token_tag_pairs.append((token, tag))

    (last_tag, lastToken, last_TAT) = (tag, token, TAT)

  res = ''
  for (token, tag) in token_tag_pairs:
    res += token + '/' + tag + ' '
  return res[:-1]

def pre_parse():
  """Prepares the review text for parsing"""
  multiword_attrs = set((a, b) for [a, b] \
    in load_json('./data/multiword_attributes.json')["multiword_attributes"])

  written_sentences = CHUNK_SIZE + 1
  out = None
  outfile_num = 0
  files = os.listdir('./data/tagged')
  ll = LoopLogger(1000, len(files), True)
  for filename in os.listdir('./data/tagged'):
    ll.step()
    if written_sentences > CHUNK_SIZE:
      written_sentences = 0
      outfile_num += 1
      out = open('./data/to_parse/to_parse_' + str(outfile_num), 'w')

    out.write("\nFNAME:" + filename + '/NN\n')
    for sentence in open('./data/tagged/' + filename):
      out.write(combine_multi_words(sentence, multiword_attrs))
      written_sentences += 1

if __name__ == '__main__':
  pre_parse()
