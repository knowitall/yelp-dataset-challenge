import json
from time import time

def load_json(fname):
  """Reads the JSON data in fname and returns it as a dictionary"""
  with open(fname) as f:
    return json.loads(f.read())

def write_json(d, fname):
  """Writes dictionary d to fname"""
  with open(fname, 'w') as f:
    f.write(json.dumps(d))

def load_json_lines(fname):
  """Yields the JSON data in fname, which should have one JSON object per line"""
  with open(fname) as f:
    for line in f:
      yield json.loads(line)

def min_argmin(f, args):
  """Returns the min value and argmin of f in a tuple"""
  return min((f(a), a) for a in args)

class NestedDict(dict):
  """Dictionary with unlimited nesting"""
  def __getitem__(self, key):
    if key in self: return self.get(key)
    return self.setdefault(key, NestedDict())

class LoopLogger():
  """Class for printing out the progress of iteration"""
  def __init__(self, step_size, size=0, print_time=False):
    self.step_size = step_size
    self.size = size
    self.n = 0
    self.print_time = print_time

  def step(self):
    if self.n == 0:
      self.start_time = time()

    self.n += 1
    if self.n % self.step_size == 0:
      if self.size == 0:
        print 'On item ' + str(self.n)
      else:
        print 'On item ' + str(self.n) + ' out of ' + str(self.size)
        if self.print_time and (self.n % (self.step_size * 10)) == 0:
          time_elapsed = time() - self.start_time
          print "Time elapsed: {:.2f}".format(time_elapsed)
          time_per_step = time_elapsed / self.n
          print "Time remaining: {:.2f}".format((self.size - self.n) * time_per_step)
