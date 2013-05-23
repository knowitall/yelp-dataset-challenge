import os
import subprocess
import time
import sys

from multiprocessing import Process, Manager, Lock

IN_DIR = './data/to_parse'
OUT_DIR = './data/parsed'
OUT_NAME = 'parsed'
TMP_NAME = 'tmp'

def parse(completed, lock):
  """Runs the parser mogura on the remaining files in to_parse
  There is an extra step of creating a temporary file so if we halt the
  program, the partial work the parser has done on a given file is thrown out
  """
  while True: # bit of a hack, hangs forever when parsing is done
    for infilename in os.listdir(IN_DIR):
      infile = IN_DIR + '/' + infilename
      outname = OUT_NAME + '_' + infilename.rsplit('_', 1)[1]
      outfile = OUT_DIR + '/' + outname
      tmpname = TMP_NAME + infilename.rsplit('_', 1)[1]
      tmpfile = OUT_DIR + '/' + tmpname

      with lock:
        if outname in completed:
          continue
        completed[outname] = 0

      print "ON FILE " + infilename
      subprocess.call('./external/mogura -nt < '
                      + infile + ' > ' + tmpfile, shell=True)
      subprocess.call('mv ' + tmpfile + ' ' + outfile, shell=True)

def parse_parallel(num_processes):
  """Runs parse on num_processes separate processes"""
  manager = Manager()

  completed = manager.dict()
  for filename in os.listdir(OUT_DIR):
    completed[filename] = 0

  lock = Lock()
  procs = [Process(target=parse, args=(completed, lock)) for i in range(num_processes)]
  for p in procs: p.start()
  for p in procs: p.join()

if __name__ == '__main__':
  parse_parallel(4)
