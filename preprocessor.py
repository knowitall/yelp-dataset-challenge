from util import *

REVIEW_DATA_FILE = './data/yelp_phoenix_academic_dataset/' + \
                   'yelp_academic_dataset_review.json'
BUSINESS_DATA_FILE = './data/yelp_phoenix_academic_dataset/' + \
                     'yelp_academic_dataset_business.json'

def split_reviews():
  """Splits the review text across multiple files, one per review.
  Only reviews about restaurants are kept.
  Unfortunately splitting the review_data over many files makes some steps slow,
  but this makes running external tools over the data much easier.
  """
  restaurants = set()
  for business_data in load_json_lines(BUSINESS_DATA_FILE):
    if "Restaurants" in business_data["categories"]:
      restaurants.add(business_data["business_id"])

  ll = LoopLogger(1000, 229907, True)
  for review_data in load_json_lines(REVIEW_DATA_FILE):
    ll.step()
    if review_data['business_id'] in restaurants:
      with open('./data/reviews/' + review_data['review_id'], 'w') as o:
        o.write((review_data['text'] + '\n').encode('utf8'))

def build_review_businesses():
  """Creates a json object taking review ids to the business id of their
  subject.
  """
  restaurants = set()
  for business_data in load_json_lines(BUSINESS_DATA_FILE):
    if "Restaurants" in business_data["categories"]:
      restaurants.add(business_data["business_id"])

  review_businesses = {}
  for review_data in load_json_lines(REVIEW_DATA_FILE):
    review_businesses[review_data['review_id']] = review_data['business_id']
  write_json(review_businesses, './data/review_businesses.json')

def preprocess():
  """Runs preprocessing over the yelp dataset"""
  build_review_businesses()
  split_reviews()

if __name__ == '__main__':
  preprocess()
