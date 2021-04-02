import argparse
import math
import matplotlib
import matplotlib.pyplot as plt
import os
import pandas as pd
import progressbar

from git import Repo

parser = argparse.ArgumentParser(description='Analyse software entropy of a repository.')
parser.add_argument('--repo', dest='path', help='Path to the repository to analyze', required=True)
parser.add_argument('--branch', dest='branch', help='Repository branch to analyze', default='master')
parser.add_argument('--max-count', dest='max_count', help='Maximum number of commits to analyze', type=int, default=10000)
parser.add_argument('--avg-window', dest='avg_window', help='Averaging window size', type=int, default=50)
args = parser.parse_args()

repo = Repo(os.path.abspath(args.path))
repo.git.checkout(args.branch)
commit = repo.head.commit

entropy_entries = {
    'datetime': [],
    'entropy': [],
}

bar = progressbar.ProgressBar(max_value=args.max_count)

while (len(entropy_entries['entropy']) < args.max_count):

    time_of_entropy = commit.committed_datetime
    entropy_of_commit = commit.stats.total['files']

    entropy_entries['datetime'].append(time_of_entropy)
    entropy_entries['entropy'].append(entropy_of_commit)

    bar.update(len(entropy_entries['entropy']))

    commit = commit.parents[0]

entropy_entries['datetime'].reverse()
entropy_entries['entropy'].reverse()

df = pd.DataFrame(entropy_entries)
df['entropy_moving_average'] = df.iloc[:,1].rolling(window=args.avg_window).mean()
df['entropy_cumulative_average'] = df.iloc[:,1].expanding().mean()

x_data = matplotlib.dates.date2num(df['datetime'])

plt.figure(1)

p = plt.subplot(2, 1, 1)
plt.plot_date(x_data, df['entropy'], 'b-', label='Raw Data')
plt.yscale('log')
plt.autoscale(True)
plt.grid()
plt.legend()

plt.subplot(2, 1, 2)
plt.plot_date(x_data, df['entropy_moving_average'], 'r-', label='Moving Average')
plt.plot_date(x_data, df['entropy_cumulative_average'], 'g-', label='Cumulative Average')
plt.yscale('log')
plt.autoscale(True)
plt.grid()
plt.legend()

plt.show()
