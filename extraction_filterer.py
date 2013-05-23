from util import *

def filter_extractions():
  """Reads in the detailed raw extractions. Then filters out the uncommon ones
  (i.e. not in extractions_common) and irrelevant ones (i.e. classified as
  "None")"""

  extractions_detailed = load_json('./data/extractions_detailed.json')
  extractions_common = load_json('./data/common_extractions.json')
  attr_categories = load_json('./data/attr_categories.json')

  extractions_final = NestedDict()
  for p in extractions_common:
    for a in extractions_common[p]:
      if attr_categories[a] == 'Irrelevant':
        continue
      for v in extractions_common[p][a]:
        extractions_final[p][a][v] = extractions_detailed[p][a][v]

  write_json(extractions_final, './data/extractions_final.json')


if __name__ == '__main__':
  filter_extractions()
