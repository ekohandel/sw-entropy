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
head = repo.create_head(args.branch)
commit = head.commit

entropy_entries = {
    'datetime': [],
    'entropy': [],
}

bar = progressbar.ProgressBar(max_value=args.max_count)

while (len(entropy_entries['entropy']) < args.max_count):

    number_of_changed_files = commit.stats.total['files']
    entrop_of_commit = 0
    try:
        entropy_of_commit = math.log(number_of_changed_files, 2)
    except:
        pass
    time_of_entropy = commit.committed_datetime

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

plt.subplot(3, 1, 1)
plt.plot_date(x_data, df['entropy'], 'b-', label='Raw Data')
plt.autoscale(True)
plt.grid()
plt.legend()

plt.subplot(3, 1, 2)
plt.plot_date(x_data, df['entropy_moving_average'], 'r-', label='Moving Average')
plt.autoscale(True)
plt.grid()
plt.legend()

plt.subplot(3, 1, 3)
plt.plot_date(x_data, df['entropy_cumulative_average'], 'g-', label='Cumulative Average')
plt.autoscale(True)
plt.grid()
plt.legend()

plt.show()
