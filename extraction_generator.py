import os
import json
import nltk
from util import *

PARSE_DIR = './data/parsed/'
FILE_PREFIX = 'parsed'

def process_sentence(review, sentence_num, sentence_info, extractions):
  '''Given the result of the parser over a sebtence, extract adjective and
  negation relations. review and sentence_num are to keep track of where
  the extraction came from.
  '''
  possible = [] # possible extraction
  adj = [] # indices of values of possible
  verb = {} # arg_index -> pred_index
  negated = set() # arg_indices

  for info in sentence_info:
    pred = info[0]
    pred_base = info[1]
    pred_pos = info[2]
    pred_ind = info[4]
    pred_type = info[5]
    arg = info[7]
    arg_pos = info[9]
    arg_ind = info[11]

    if 'adj_arg' in pred_type \
        and ('JJ' in pred_pos or 'V' in pred_pos) \
        and 'NN' in arg_pos:
      attr = ' '.join(arg.split('#')).lower()
      value = pred.lower()
      possible.append((attr, value))
      adj.append(pred_ind)
    elif pred_base == 'not':
      negated.add(arg_ind)
    elif 'verb_arg' in pred_type:
      verb[arg_ind] = pred_ind

  for i in range(len(possible)):
    attr, value = possible[i]
    if adj[i] in negated or adj[i] in verb and verb[adj[i]] in negated:
      value = '!' + value
    extractions[review][sentence_num][unicode(attr, errors='ignore')] \
                                     [unicode(value, errors='ignore')] = 1

def get_raw_extractions():
  """Reads in the output of the parser and returns a nested dict taking
  review id -> sentence number -> attribute -> value
  """
  raw_extractions = NestedDict()
  for infilename in os.listdir(PARSE_DIR):
    if FILE_PREFIX not in infilename:
      continue
    print "On file " + infilename
    review = ''
    with open(PARSE_DIR + '/' + infilename) as f:
      sentence_num = 0
      sentence_info = []
      for line in f:
        info = line.rstrip().split('\t')
        if len(info) != 12:
          if sentence_num != 0 and len(sentence_info) > 0:
            process_sentence(review, sentence_num, sentence_info, raw_extractions)
            sentence_info = []
            sentence_num += 1
        elif 'FNAME' in info[7]:
          review = info[7][6:]
          sentence_num = 0
        else:
          if sentence_num == 0:
            sentence_num = 1
          sentence_info.append(info)
  return raw_extractions

def get_unstemmed_extractions(raw_extractions):
  """Given a nested dict of "raw" extractions taking
    review id -> sentence number -> attribute -> value
  return a nested dict taking
    business_id -> attribute -> value -> list of [sentence, review id] tuples
  """
  review_businesses = load_json('./data/review_businesses.json')

  unstemmed_extractions = NestedDict()
  ll = LoopLogger(200, len(raw_extractions), True)
  for review in raw_extractions:
    ll.step()
    place = review_businesses[review]
    with open('./data/untagged' + '/' + review) as f:
      n = 0
      for line in f:
        n += 1
        if n in raw_extractions[review]:
          for attr in raw_extractions[review][n]:
            for value in raw_extractions[review][n][attr]:
              unstemmed_extractions[place][attr].setdefault(value, []) \
                .append([unicode(line, errors='ignore'), review])
  return unstemmed_extractions

def get_stem_info(unstemmed_extractions):
  """ Takes a dictionary of extractions as produced by get_unstemmed_extractions,
  returns two dictionaries:
    1. attr_to_stem, taking each attribute to the its stem
    2. stem_to_common_attr, taking each stem to the most common attribute with
       that stem
  """
  attr_to_stem = {}
  stem_to_counts = NestedDict()
  for place in unstemmed_extractions:
    for attr in unstemmed_extractions[place]:
      c = 0
      for value in unstemmed_extractions[place][attr]:
        c += len(unstemmed_extractions[place][attr][value])
      attr = attr.lower()
      if attr in attr_to_stem:
        stem = attr_to_stem[attr]
      else:
        stem = nltk.stem.porter.PorterStemmer().stem(attr)
        attr_to_stem[attr] = stem
      stem_to_counts[stem][attr] = stem_to_counts[stem].get(attr, 0) + c

  stem_to_common_attr = {}
  for stem in stem_to_counts:
    max_count = -1
    for attr in stem_to_counts[stem]:
      if stem_to_counts[stem][attr] > max_count:
        max_count = stem_to_counts[stem][attr]
        stem_to_common_attr[stem] = attr

  return attr_to_stem, stem_to_common_attr

def get_extractions_detailed(unstemmed_extractions):
  """Takes in a dictionary of unstemmed extactions,
  as produced by get_unstemmed_extractions, returns a dictionary
  of the extractions with attributes sharing a stem combined"""
  attr_to_stem, stem_to_common_attr = get_stem_info(unstemmed_extractions)

  extractions_detailed = NestedDict()
  for place in unstemmed_extractions:
    for attr in unstemmed_extractions[place]:
      stem = attr_to_stem[attr.lower()]
      attr_c = stem_to_common_attr[stem]
      for value in unstemmed_extractions[place][attr]:
        value_c = value.lower()
        extractions_detailed[place][attr_c].setdefault(value, []) \
          .extend(unstemmed_extractions[place][attr][value])
  return extractions_detailed

def get_extractions(extractions_detailed):
  """Goes from the detailed extractions taking
    business_id -> attribute -> value -> list of [sentence, review id] tuples
  to a smaller dictionary taking
    business_id -> attribute -> value -> value count
  """
  extractions = NestedDict()
  for place in extractions_detailed:
    for attr in extractions_detailed[place]:
      for value in extractions_detailed[place][attr]:
        extractions[place][attr][value] = \
          len(extractions_detailed[place][attr][value])
  return extractions

def generate_extractions():
  """Generates a json file of extractions from the parser output"""
  print 'Generating raw extractions...'
  raw_extractions = get_raw_extractions()
  print 'Getting unstemmed extractions...'
  unstemmed_extractions = get_unstemmed_extractions(raw_extractions)
  print "Generating stemmed extractions"
  extractions_detailed = get_extractions_detailed(unstemmed_extractions)
  print "Generating lite extractions"
  extractions = get_extractions(extractions)
  print "Writing extractions"
  write_json(extractions_detailed, './data/extractions_detailed.json')
  write_json(extractions, './data/extractions.json')

if __name__ == '__main__':
  generate_extractions()
