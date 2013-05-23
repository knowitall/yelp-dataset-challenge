Opinion Mining over the Yelp Challenge Dataset
--------

This system induces a set of extractions, which are in the form of attribute-value pairs, from restaurant reviews. Attributes are features of the restaurant discussed in the review (e.g. chicken, service, atmosphere) and values are descriptors of the attributes (e.g. delicious, fast, romantic). Each value has an associated polarity (how positive or negative it is). Attributes are clustered into five categories: Food, Service, Decor, Overall, and Other. The project was build as an entrant to the [Yelp Dataset Challenge][ydc] by Kevin Clark.

### Related Work
The system was built as a new extraction algorithm for RevMiner, a user iterface using extractions to provide quality search and summarization of restaurants. RevMiner is a University of Washington [KnowItAll][knowitall] project by [Jeff Huang][jeff], [Oren Etzioni][oren], [Luke Zettlemoyer][luke], Kevin Clark, and Christian Lee. The work on RevMiner was [published][paper] in UIST 2012.

### Demo

A demo of the opinion mining algorithm's output over the Yelp Challenge Dataset, is available at http://ec2-54-226-72-101.compute-1.amazonaws.com/#jade%20palace. The extractions are displayed using displayed using RevMiner's UI.


### Requirements

* Python 2.6-2.7
* NLTK 2.0
* scikit-learn 0.13 or later
* The Stanford POS Tagger 3.0
* Enju 2.4.2

### Usage
Use extractor.py to run the full opinion mining pipeline. It is also possible to run the scripts individually (in the same order as in extractor.py).

Be warned, some steps are quite slow and create a significant amount of intermediary data (particularly the parsing).

The final output files are:

 * **data/extractions_final.json**: A JSON object taking business ids to attributes to values to a list of [sentence, review id] tuples giving the source of each extraction.
 * **data/attr_categories.json**: A JSON object taking attributes to categories ("Food", "Service", "Decor", "Overall", "Other", or "None")
 * **data/polarities.json**: A JSON object taking values to polarity values (between 1 and 5).

The resulting output files after running the extractor over the Yelp Challenge Dataset are included in this repository.

[knowitall]: http://www.cs.washington.edu/research/knowitall
[jeff]: http://jeffhuang.com/
[oren]: http://www.cs.washington.edu/homes/etzioni
[luke]: http://www.cs.washington.edu/homes/lsz/
[paper]: http://jeffhuang.com/revminer_uist2012_preprint.pdf
[ydc]: http://www.yelp.com/dataset_challenge/

