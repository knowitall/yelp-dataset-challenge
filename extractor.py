import subprocess
import preprocessor
import multiword_attr_identifier
import parser_preparation
import parser 
import extraction_generator
import common_extraction_generator
import attribute_classifier
import extraction_filterer
import polarity_computer

def run_extractor():
  """Run the full extraction pipeline"""
  
  subprocess.call('mkdir data/reviews', shell=True)
  subprocess.call('mkdir data/tagged', shell=True)
  subprocess.call('mkdir data/untagged', shell=True)
  subprocess.call('mkdir data/to_parse', shell=True)
  subprocess.call('mkdir data/parsed/', shell=True)
  
  preprocessor.preprocess()
  
  subprocess.call('javac -cp ./external/stanford-postagger.jar Tagger.java', shell=True)
  subprocess.call('java -cp ".:./external/stanford-postagger.jar" -Xmx1024m Tagger ./external/left3words-wsj-0-18.tagger data/reviews data/tagged data/untagged', shell=True)
  
  multiword_attr_identifier.identify_multiword_attrs()
  parser_preparation.pre_parse()
  parser.parse_parallel(4)
  extraction_generator.generate_extractions()
  common_extraction_generator.generate_common_extractions()
  attribute_classifier.classify()
  extraction_filterer.filter_extractions()
  polarity_computer.compute_polarities()

if __name__ == '__main__':
  run_extractor()
