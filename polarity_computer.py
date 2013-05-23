from util import *
from collections import Counter

REVIEW_DATA_FILE = './data/yelp_phoenix_academic_dataset/' + \
                   'yelp_academic_dataset_review.json'

def compute_polarities():
  """Compute the polarity of each value in the final extraction set by
  averaging the stars of all reviews that value appeared in
  """
  stars = {}
  for review_data in load_json_lines(REVIEW_DATA_FILE):
    stars[review_data['review_id']] = float(review_data['stars'])

  value_scores = Counter()
  value_counts = Counter()
  extractions = load_json('./data/extractions_final.json')
  for p in extractions:
    for a in extractions[p]:
      for v in extractions[p][a]:
        for [s, r] in extractions[p][a][v]:
          value_scores[v] += stars[r]
          value_counts[v] += 1

  for v in value_scores:
    value_scores[v] /= value_counts[v]

  write_json(value_scores, './data/polarities.json')

if __name__ == '__main__':
  compute_polarities()
