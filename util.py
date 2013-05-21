import json
from time import time

def load_json(fname):
  with open(fname) as f:
    return json.loads(f.read())

def write_json(j, fname):
  with open(fname, 'w') as f:
    f.write(json.dumps(j))

def load_json_lines(fname):
  with open(fname) as f:
    for line in f:
      yield json.loads(line)

class NestedDict(dict):
  def __getitem__(self, key):
    if key in self: return self.get(key)
    return self.setdefault(key, NestedDict())

class LoopLogger():
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
          print "Time elapsed: " + str(time_elapsed)
          time_per_step = time_elapsed / self.n
          print "Time remaining: " + str((self.size - self.n) * time_per_step)
