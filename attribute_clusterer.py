import itertools
import json
import math
import random

from util import *
from operator import itemgetter

# Smoothing value for Kullback-Leibler divergence
KL_SMOOTHING = 0.5

# Being a bit hacky with some global vars
attrs = set()
attr_value_counts = {}
attr_value_ratios = {}
attr_counts = {}
value_counts = {}

def KL_divergence(value_counts1, value_counts2):
  """Returns the Kullback-Leibler divergence between the two distributions"""
  divergence = 0
  s1 = sum([value_counts1[value] for value in value_counts1])
  s2 = sum([value_counts2[value] for value in value_counts2])
  for value in set(value_counts1).union(value_counts2):
    assert(value in value_counts1 or value in value_counts2)
    if value not in value_counts1:
      s1 += KL_SMOOTHING
    if value not in value_counts2:
      s2 += KL_SMOOTHING
  for value in set(value_counts1).union(value_counts2):
    v1 = v2 = KL_SMOOTHING
    if value in value_counts1:
      v1 = value_counts1[value]
    if value in value_counts2:
      v2 = value_counts2[value]
    v1 = float(v1) / s1
    v2 = float(v2) / s2
    divergence += v1 * math.log(v1 / v2)
  if divergence > math.e:
    divergence = math.e
  return divergence

def load_attribute_data():
  """Computes some useful statistics about the attributes in 
  common_extractions
  """
  global attr_value_counts, attr_counts, value_counts, \
    attr_value_ratios, attrs

  print "Loading extraction data..."
  with open('./data/common_extractions.json') as f:
    place_data = json.loads(f.read())
    for place in place_data:
      for attr in place_data[place]:
        if attr not in attr_value_counts:
          attrs.add(attr)
          attr_value_counts[attr] = {}
          attr_counts[attr] = 0
        for value in place_data[place][attr]:
          c = place_data[place][attr][value]
          value_counts[value] = value_counts.get(value, 0) + c
          attr_counts[attr] += c
          attr_value_counts[attr][value] = \
            attr_value_counts[attr].get(value, 0) + c
  
  for attr in attrs:
    attr_value_ratios[attr] = {}
    for value in attr_value_counts[attr]:
      attr_value_ratios[attr][value] = float(attr_value_counts[attr][value]) \
                                       / attr_counts[attr]

distances = {}
symmetric_distances = {}
def load_distances(filename):
  """Loads the distances between each pair of attributes"""
  global distances, symmetric_distances, attrs

  print "Loading distances from " + filename + "..."
  distances = load_json(filename)

  symmetric_distances = {p: {} for p in distances}
  for (p1, p2) in itertools.combinations(distances, 2):
    symmetric_distances[p1][p2] = symmetric_distances[p2][p1] = \
      (distances[p1][p2] + distances[p2][p1]) / 2

  for p in distances:
    symmetric_distances[p][p] = 0
  attrs = distances.keys()

def write_distances(filename):
  """Computes the distance between each pair of attributes using KL divergence"""
  print "Computing distances and writing to " + filename +  "..."
  distances = {}
  n = 0

  for a1 in attrs:
    distances[a1] = {}
    n += 1
    print "On point " + str(n) + " out of " + str(len(attrs))
    for a2 in attrs:
      distances[a1][a2] = KL_divergence(attr_value_counts[a1],
                                        attr_value_counts[a2])

  with open(filename, 'w') as f:
    f.write(json.dumps(distances))

def average_distance(c1, c2):
  """Returns the average distance between the two sets of attributes"""
  return sum(sum(symmetric_distances[p1][p2] for p1 in c1) for p2 in c2) \
         / (len(c1) * len(c2))

def sorted_clusters(clusters, distance_function):
  """Sort the attributes in each cluster by how "central" they are"""
  return [sorted([p for p in c], key = lambda p:
     distance_function(set([p]), c)) for c in clusters]

def iterative_cluster(clusters, points, distance_function, max_iterations=1000):
  """Iteratively cluster points into clusters using the distance function"""
  point_assignments = {p: 0 for p in points}

  for p in points:
    if p not in symmetric_distances:
      print p

  for n in range(max_iterations):
    assignment_change = False
    new_clusters = [set() for c in clusters]

    for p in points:
      (score, i) = min_argmin(
        lambda i: distance_function(set([p]), clusters[i]),
        range(len(clusters)))
      if point_assignments[p] != i:
        point_assignments[p] = i
        assignment_change = True
      new_clusters[i].add(p)

    clusters = new_clusters
    if not assignment_change: break

  return sorted_clusters(clusters, distance_function)

# Maps each category to an integer
category_mapping = \
  {'None': 0, 'Food': 1, 'Service': 2, 'Decor': 3, 'Overall': 4}
# Inverse of category_mapping
inverse_category_mapping =  dict([[v,k] for k,v in category_mapping.items()])
# Maps hand label annotations to categories
abbreviation_mapping = {
  'n': 'None', 'f': 'Food', 's': 'Service',
  'd': 'Decor', 'o': 'Overall'}

category_distances = NestedDict()
def categorize(seeds):
  """Categorize the attributes according to the seeds"""
  global category_distances
  attr_by_category = {c: [] for c in seeds}
    
  distance = lambda a, c: min(distances[seed][a] for seed in seeds[c])
  for attr in attrs:
    for c in seeds:
      category_distances[attr][c] = distance(attr, c)

    (score, category) = min_argmin(
      lambda c: distance(attr, c), seeds)
    attr_by_category[category].append((attr, score))

  return {c: sorted(attr_by_category[c], key=itemgetter(1))
          for c in attr_by_category}

attr_categories = {}
seeds = {}
def categorize_attributes():
  """Categorize all the attributes"""
  global attr_categories, seeds
  print "Generating seeds..."
  seeds = get_seeds()

  print "Categorizing attributes..."
  categorized = categorize(seeds)
  
  category_distances = {}
  attr_categories = {}
  for c in categorized:
    for (attr, score) in categorized[c]:
      attr_categories[attr] = c
      category_distances[attr] = score

def get_seeds():
  """Compute seeds for each category using a clustering algorithm"""
  num_clusters = {'Food': 5, 'Decor': 5, 'Service': 5, 
                  'Overall': 5, 'None': 10}

  e, y = get_labeled_data('./data/labeled_attributes/develop_set')
  clusters = [set() for i in range(len(category_mapping))]
  for i in range(len(e)):
    clusters[y[i]].add(e[i])

  # In order to pick seeds that cover each category well, cluster the labeled 
  # attrs in each category and take the centers of those clusters as seeds
  seeds = {}
  for i in range(len(clusters)):
    category = inverse_category_mapping[i]
    c = clusters[i]
    l = list(c)
    initial = [set([l[j]]) for j in range(num_clusters[category])]
    subclusters = iterative_cluster(initial, c, average_distance, 40)
    seeds[category] = [s[0] for s in subclusters]

  return seeds

def evaluate(attr_categories, print_errors=True):
  """Evaluate our classification against the test set"""
  e, y = get_labeled_data('./data/labeled_attributes/test_set')
 
  errors = []
  p = []
  i = 0
  for attr in e: 
    p.append(category_mapping[attr_categories[attr]])
    if p[i] != y[i]:
      errors.append((attr, inverse_category_mapping[p[i]],
                  inverse_category_mapping[y[i]]))
    i += 1

  if print_errors:
    print "SOME ERRORS: "
    print "In the form (attribute, prediction, target)"
    for elem in errors[:25]:
      print elem

  print 80 * '='
  print "METRICS:"
  print "Precision = Recall = f1 = " + \
    str(float(sum([1 for i in range(len(y)) if y[i] == p[i]])) / len(y))

def get_labeled_data(filename):
  """Load a list of examples and their labels for the given file"""
  e = []
  y = []
  with open(filename) as f:
    for line in f:
      e.append(line[1:-1])
      y.append(category_mapping[abbreviation_mapping[line[0]]])
  return e, y

def run_categorizer():
  """Runs attribute classification"""
  load_attribute_data()
  #write_distances('./data/attr_KL_divergences.json')
  load_distances('./data/attr_KL_divergences.json')
  categorize_attributes()

if __name__ == '__main__':
  run_categorizer()
  baseline_categories = {}
  for attr in attrs:
    baseline_categories[attr] = 'None'
  print 80 * '='
  print "BASELINE RESULTS:"
  evaluate(baseline_categories, False)
  print 80 * '='
  print "SEEDS:"
  print seeds
  print 80 * '='
  print "UNSUPERVISED CLUSTERING RESULTS:"
  evaluate(attr_categories)
  print 80 * '='
