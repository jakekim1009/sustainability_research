import numpy as np
import argparse

#################################################################################

parser = argparse.ArgumentParser(description='Parse Caffe log and save in human-readable form')
parser.add_argument('logfile', type=str, help='Log file path')
parser.add_argument('train_outfile', type=str, help='Training output file path')
parser.add_argument('test_outfile', type=str, help='Test output file path')

# Get arguments
args = parser.parse_args()
logfile = args.logfile
train_outfile = args.train_outfile
test_outfile = args.test_outfile

# Keep track of:
train_iters = []
train_acc = []
train_loss = []
train_learn_rates = []
test_iters = []
test_acc = []
test_loss = []

# Iterate through log line by line
with open(logfile, 'r') as f:
  for line in f:
    if 'Iteration' in line:
      if ('lr' not in line) and ('Testing' not in line):
        toks = line.split()
        idx = toks.index('Iteration') + 1
        train_iters.append(int(toks[idx][:-1]))
      elif 'lr' in line:
        toks = line.split()
        idx = toks.index('lr') + 2
        train_learn_rates.append(float(toks[idx]))
      elif 'Testing' in line:
        toks = line.split()
        idx = toks.index('Iteration') + 1
        test_iters.append(int(toks[idx][:-1]))
    elif 'Train net output' in line:
      if 'acc' in line:
        toks = line.split()
        idx = toks.index('acc') + 2
        train_acc.append(float(toks[idx]))
      elif 'loss' in line:
        toks = line.split()
        idx = toks.index('loss') + 2
        train_loss.append(float(toks[idx]))
    elif 'Test net output' in line:
      if 'acc' in line:
        toks = line.split()
        idx = toks.index('acc') + 2
        test_acc.append(float(toks[idx]))
      elif 'loss' in line:
        toks = line.split()
        idx = toks.index('loss') + 2
        test_loss.append(float(toks[idx]))

# Print lengths
print 'Train iters: {}'.format(len(train_iters))
print '  Acc: {}'.format(len(train_acc))
print '  Loss: {}'.format(len(train_loss))
print '  LR: {}'.format(len(train_learn_rates))
print 'Test iters: {}'.format(len(test_iters))
print '  Acc: {}'.format(len(test_acc))
print '  Loss: {}'.format(len(test_loss))

# Save training log
with open(train_outfile, 'w') as f:
  for idx, iteration in enumerate(train_iters):
    try:
      data = str(iteration) + ' ' + str(train_acc[idx]) + ' ' + str(train_loss[idx]) + ' ' + str(train_learn_rates[idx]) + '\n'
      f.write(data)
    except:
      pass

# Save test log
with open(test_outfile, 'w') as f:
  for idx, iteration in enumerate(test_iters):
    try:
      data = str(iteration) + ' ' + str(test_acc[idx]) + ' ' + str(test_loss[idx]) + '\n'
      f.write(data)
    except:
      pass