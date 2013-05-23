import json
from operator import itemgetter

from attribute_clusterer import *
from util import *

import numpy as np
import pylab as pl

import random

from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.feature_extraction import DictVectorizer

def get_features(attr, common_values):
  """Returns the features for the given attribute in a dictionary"""
  features = {}
  common_count = 1
  for value, c in common_values:
    if value in attr_value_counts[attr]:
      features[value] = attr_value_counts[attr][value]
      common_count += attr_value_counts[attr][value]
    else:
      features[value] = 0

  # Relative frequency of the most common associated adjectives
  for value, c in common_values:
    features[value] = float(features[value]) / common_count

  # Total number of extractions with this noun
  features['total_count'] = attr_counts[attr]

  # What percentage of the extractions with this noun occur with the common
  # adjectives
  features['count_ratio'] = float(common_count) / attr_counts[attr]

  # Cluster distances from attributeclusterer
  for category in category_distances[attr]:
    features[category + '_distance'] = category_distances[attr][category]

  return features

def classify_all(clf, X, examples):
  """Runs the given classifier over the whole data set"""
  p = clf.predict(X)
  for i in range(len(examples)):
    attr_categories[examples[i]] = inverse_category_mapping[p[i]]

def X_y(filename, feature_dicts, vectorizer, examples):
  """Get the features and labels from the given file"""
  e, y = get_labeled_data(filename)
  X = vectorizer.transform([feature_dicts[examples.index(ex)] for ex in e])
  return X, y

feature_dicts = {}
def classify():
  """Classify all attrs"""
  run_categorizer()

  # Find the most common values for features
  common_values = set(sorted( \
    value_counts.items(), key=itemgetter(1), reverse=True)[:40])

  # Compute the features
  feature_dicts = []
  examples = list(attrs)
  for attr in examples:
    feature_dicts.append(get_features(attr, common_values))
  vectorizer = DictVectorizer(sparse=False)
  X = vectorizer.fit_transform(feature_dicts)

  # Gather the training data and train a random forest classifier on it
  X_train, y_train = X_y('./data/labeled_attributes/develop_set',
                         feature_dicts, vectorizer, examples)
  clf = ExtraTreesClassifier(n_estimators=100)
  clf.fit(X_train, y_train)

  '''importances = clf.feature_importances_
  print clf
  print importances
  feature_scores = []
  feature_names = vectorizer.get_feature_names()
  for i in range(len(importances)):
    feature_scores.append((feature_names[i], importances[i]))
  for pair in sorted(feature_scores, key=itemgetter(1), reverse=True):
    print pair'''

  # Classify everything, print out metrics and write the results
  classify_all(clf, X, examples)

  print 80 * '='
  evaluate(attr_categories)
  print 80 * '='

  # Use the hand labels when available
  e, y = get_labeled_data('./data/labeled_attributes/develop_set')
  e_test, y_test = get_labeled_data('./data/labeled_attributes/test_set')
  e.extend(e_test)
  y.extend(y_test)

  for target, attr in zip(y, e):
    attr_categories[attr] = inverse_category_mapping[target]

  write_json(attr_categories, './data/attr_categories.json')

if __name__ == '__main__':
  classify()
