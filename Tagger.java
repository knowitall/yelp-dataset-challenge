mport java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.BufferedWriter;
import java.io.File;
import java.util.ArrayList;
import java.util.List;

import edu.stanford.nlp.ling.Sentence;
import edu.stanford.nlp.ling.TaggedWord;
import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.tagger.maxent.MaxentTagger;
import edu.stanford.nlp.process.PTBTokenizer;

/**
 *  Runs the Stanford POS Tagger over the files in the provided directory
 *  Outputs both the tagged sentences and sentence-tokenized sentences
 */
class Tagger {
  public static void main(String[] args) throws Exception {
    if (args.length != 4) {
      System.err.println("usage: java Tagger reviewsDir taggedDir untaggedDir");
      return;
    }
    MaxentTagger tagger = new MaxentTagger(args[0]);
    @SuppressWarnings("unchecked")

    File dir = new File(args[1]);
    String[] children = dir.list();
    if (children == null) {
      // Either dir does not exist or is not a directory
      System.out.println("No such directory: " + args[1]);
    } else {
      for (int i=0; i<children.length; i++) {
        String filepath = args[1] + '/' + children[i];
        BufferedWriter out = new BufferedWriter(new FileWriter(args[2] + '/' + children[i]));
        BufferedWriter out2 = new BufferedWriter(new FileWriter(args[3] + '/' + children[i]));
        List<ArrayList<? extends HasWord>> sentences = tagger.tokenizeText(new BufferedReader(new FileReader(filepath)));
        for (ArrayList<? extends HasWord> sentence : sentences) {
          ArrayList<TaggedWord> tSentence = tagger.tagSentence(sentence);
          out.write(Sentence.listToString(tSentence, false));
          out.newLine();
          out2.write(PTBTokenizer.labelList2Text(sentence));
          out2.newLine();
        }
        out.close();
        out2.close();
      }
    }
  }
}
