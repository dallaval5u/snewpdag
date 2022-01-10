"""
SNEWPDAG application.

See README for details of the configuration and input data files.
"""

import os, sys, argparse, json, logging, importlib, ast, csv
import numpy as np
from . import Node
#add mu own import path for now
#sys.path.insert(1, '/home/riccardo/Documents/GitHub/snewpdag')
from snewpdag import dag
#import snewpdag.dag.app
from hop import stream
#from . import snews_pt_utils
#from hop.io import StartPosition
#sys.path.insert(1, '/home/riccardo/SNEWS_Publishing_Tools/SNEWS_PT')
#import snews_pt_utils



def save_message(message, counter):
  """ Save messages to a json file.
  """
  #S = Subscriber()
  path = f'SNEWS_MSGs/'
  os.makedirs(path, exist_ok=True)
  file = path + 'subscribed_messages.json'
  # read the existing file
  try:
    data = json.load(open(file))
    if not isinstance(data, dict):
      print('Incompatible file format!')
      return None
    # TODO: deal with `list` type objects
  except:
    data = {}

  # RICCARDO: temporarily adding fields to the alert message (which I would like to receive)
  index_coincidence = str(counter)
  data['action'] = 'alert'
  data['burst_id'] = 0
  data['name'] = 'Control'
  data['coinc_id'] = 1
  data['number_of_coinc_dets'] = index_coincidence
  data['coinc' + index_coincidence] = message

  with open(file, 'w') as outfile:
    json.dump(data, outfile)


def run():
  """
  Entrypoint for main application program.
  Takes positional command-line arguments:
    config - name of JSON configuration file
    input  - name of JSON input file

  With the --jsonlines option, read from stdin assuming one json object/line.
  I know, this kind of sucks, but the alternative is importing another
  third-party module which provides more functionality than is needed here.
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('config', help='configuration py/json/csv file')
  parser.add_argument('--input', help='input data py/json file')
  parser.add_argument('--jsonlines', action='store_true',
                      help='each input line contains one JSON object to inject')
  parser.add_argument('--log', help='logging level')
  parser.add_argument('--seed', help='random number seed')
  parser.add_argument('--stream', help="read from the stream")
  args = parser.parse_args()
  alert_topic = "kafka://localhost:9092/snews.alert-test"

  if args.log:
    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
      raise ValueError('Invalid log level {}'.format(args.log))
    logging.basicConfig(level=numeric_level)

  # initialize random number generator
  if args.seed:
    Node.rng = np.random.default_rng(int(args.seed))
  else:
    Node.rng = np.random.default_rng()

  cfn, cfx = os.path.splitext(args.config)
  if cfx == '.csv':
    # name, class, observe
    with open(args.config, 'r') as f:
      nodespecs = csv_eval(f)
  else: # try python/json parsing if not csv
    with open(args.config, 'r') as f:
      nodespecs = ast.literal_eval(f.read())
    #nodes = configure(nodespecs)

  dags = {}

  if args.input:
    with open(args.input) as f:
      if args.jsonlines:
        for jsonline in f:
          data = ast.literal_eval(jsonline)
          print(data)
          inject(dags, data, nodespecs)
      else:
        data = ast.literal_eval(f.read())
        inject(dags, data, nodespecs)

  elif args.stream: #toadd
      # with stream.open(self.alert_topic, "r") as s:
      s = stream.open(alert_topic, "r") #add dependencies
      counter = 0
      for message in s:
        counter +=1
        print(message)
        save_message(message, counter)
        with open('/home/riccardo/Documents/GitHub/snewpdag/SNEWS_MSGs/subscribed_messages.json') as f:
          data = ast.literal_eval(f.read())
          print(' I am injecting this data into a dag:')
          print(data)
          if int(data['number_of_coinc_dets']) > 1:
            inject(dags, data, nodespecs)
  else:
    if args.jsonlines:
      for jsonline in sys.stdin:
        data = ast.literal_eval(jsonline)
        inject(dags, data, nodespecs)
    else:
      data = ast.literal_eval(sys.stdin.read())
      inject(dags, data, nodespecs)

def csv_eval(infile):
  # name, class, observe
  nodespecs = []
  reader = csv.reader(infile, quotechar='"')
  for row in reader:
    #print('New row:  {}'.format(row))
    if len(row) == 0:
      continue # blank line
    if row[0] == '' or row[0][0] == '#':
      continue # comment line
    if len(row) < 2:
      logging.error('Node specification requires at least 2 fields')
      continue
    node = { 'name': row[0], 'class': row[1] }
    if len(row) >= 3 and len(row[2]) > 0:
      nl = []
      ns = row[2].strip().split(',')
      for n in ns:
        s = n.strip()
        if len(s) > 0:
          nl.append(s)
      node['observe'] = nl
    if len(row) >= 4:
      s = []
      for i in range(3, len(row)):
        if len(row[i]) > 0:
          # replace special marks which might stand in for single quotes
          r = row[i].replace("’","'").replace("‘","'").replace("`","'")
          s.append(r)
      node['kwargs'] = ast.literal_eval('{' + ','.join(s) + '}')
    nodespecs.append(node)
  return nodespecs

def find_class(name):
  s = name.split('.')
  base = ['snewpdag','plugins']
  path = '.'.join(base+s[0:-1])
  cl = s[-1]
  mod = importlib.import_module(path)
  if hasattr(mod, cl):
    return getattr(mod, cl)
  else:
    logging.error('Unknown class {} in {}'.format(cl, path))
    sys.exit(2)

def configure(nodespecs):
  """
  Build DAG from configuration dictionary.
  """
  nodes = {}

  for spec in nodespecs:
    if 'class' in spec:
      c = find_class(spec['class'])
    else:
      logging.error('No class field in node specification')
      return None

    if 'name' in spec:
      name = spec['name']
    else:
      logging.error('No name field in node specification')
      return None

    if name in nodes:
      logging.error('Duplicate node name {}'.format(name))
      return None

    kwargs = spec['kwargs'] if 'kwargs' in spec else {}
    kwargs['name'] = spec['name']
    try:
      nodes[name] = c(**kwargs)
    except TypeError:
      logging.error('While creating node {0}: {1}'.format(name, sys.exc_info()))
      return None

    if 'observe' in spec:
      for obs in spec['observe']:
        if obs == name:
          logging.error('{0} observing itself'.format(name))
          return None
        elif obs in nodes:
          nodes[obs].attach(nodes[name])
        else:
          logging.error('{0} observing unknown node {1}'.format(name, obs))
          return None

  return nodes

def inject(dags, data, nodespecs):
  """
  Send data through DAG.
  If there is no burst identifier, assume it's 0.
  If the DAG doesn't exist for this burst, create a new one.
  """
  if type(data) is dict:
    print('my data is a dictionary')
    print(dags)
    inject_one(dags, data, nodespecs)
  elif type(data) is list:
    for d in data:
      inject_one(dags, d, nodespecs)
  else:
    logging.error('What is this input data?')
    sys.exit(2)

def inject_one(dags, data, nodespecs):
  burst_id = 0
  if 'burst_id' in data:
    print('burst_id is in my data')
    burst_id = data['burst_id']
    print(dags)
  if burst_id not in dags:
    print('burst_id {} is not in my data'.format(burst_id))
    dags[burst_id] = configure(nodespecs)
    if dags[burst_id] == None:
      logging.error('Invalid configuration for burst id {}'.format(burst_id))
      sys.exit(2)
  dag = dags[burst_id]
  print(dags)
  dag[data['name']].update(data)
  print('this is my dag:')
  print(dag)

