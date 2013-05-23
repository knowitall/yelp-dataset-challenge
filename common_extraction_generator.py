import json
from collections import Counter
from util import *

NUM_ATTRS = 1500
NUM_VALUES = 3000

def generate_common_extractions():
  """Reads in the raw extractions and only keeps the top NUM_ATTRS most
  common attrs and NUM_VALUES most common values. Writes the results to
  common_extractions.json.
  """

  print "Loading extractions..."
  extractions = load_json('./data/extractions.json')

  print 'Generating counts...'
  attr_counts = Counter()
  value_counts = Counter()
  for place in extractions:
    for attr in extractions[place]:
      c = 0
      for value in extractions[place][attr]:
        c += extractions[place][attr][value]
        value_counts[value] += c
      attr_counts[attr] += c

  print "Writing common attributes and values..."
  attrs = set(sorted(attr_counts.keys(),
    key = lambda a: attr_counts[a], reverse=True)[:NUM_ATTRS])
  values = set(sorted(value_counts.keys(),
    key = lambda v: value_counts[v], reverse=True)[:NUM_VALUES])

  common_extractions = NestedDict()
  for place in extractions:
    for attr in extractions[place]:
      if attr in attrs:
        for value in extractions[place][attr]:
          if value in values:
            common_extractions[place][attr][value] = extractions[place][attr][value]

  write_json(common_extractions, './data/common_extractions.json')

if __name__ == '__main__':
  generate_common_extractions()
