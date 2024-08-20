# -*- coding: utf-8 -*-
"""Recommender_Clean_Code.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1i2q6NG5pnZwLhwq9ubi2zLRtZMqJ7KGC

✅ Import Libraryes
"""

! pip install surprise
! pip install plotly
! pip install scrapbook

from google.colab import drive
drive.mount("/content/drive")

import pandas as pd
from surprise import Reader
from surprise import Dataset
from surprise.model_selection import cross_validate
from surprise import NormalPredictor
from surprise import KNNBasic
from surprise import KNNWithMeans
from surprise import KNNWithZScore
from surprise import KNNBaseline
from surprise import SVD
from surprise import BaselineOnly
from surprise import SVDpp
from surprise import NMF
from surprise import SlopeOne
from surprise import CoClustering
from surprise.accuracy import rmse
from surprise import accuracy
from surprise.model_selection import train_test_split

import os
import sys
import surprise
import scrapbook as sb
import pandas as pd

import numpy as np
import pandas as pd
from collections import Counter
from sklearn.model_selection import train_test_split
from scipy import sparse
import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

"""🎈 Import Data"""

user = pd.read_csv('/content/drive/MyDrive/colab recommender/BX-Users.csv', sep=';', error_bad_lines=False, encoding="latin-1")
user.columns = ['userID', 'Location', 'Age']
rating = pd.read_csv('/content/drive/MyDrive/colab recommender/BX-Book-Ratings.csv', sep=';', error_bad_lines=False, encoding="latin-1")
rating.columns = ['userID', 'ISBN', 'bookRating']

user.head()

rating.head()

"""## preprocessing"""

df = pd.merge(user, rating, on='userID', how='inner')
df.drop(['Location', 'Age'], axis=1, inplace=True)

df.head()

"""🔴 Explority Data Analyies"""

from plotly.offline import init_notebook_mode, plot, iplot
import plotly.graph_objs as go
from plotly.subplots import make_subplots

init_notebook_mode(connected=True)

data = df['bookRating'].value_counts().sort_index(ascending=False)
trace = go.Bar(x=data.index,
               text=['{:.1f} %'.format(val) for val in (data.values / df.shape[0] * 100)],
               textposition='auto',
               textfont=dict(color='#000000'),
               y=data.values,
               )
# Create layout
layout = dict(title='Distribution Of {} book-ratings'.format(df.shape[0]),
              xaxis=dict(title='Rating'),
              yaxis=dict(title='Count'))
# Create plot
fig = go.Figure(data=[trace], layout=layout)

# Use plot instead of iplot for Google Colab
plot(fig)

# Number of ratings per book
data = df.groupby('ISBN')['bookRating'].count().clip(upper=50)

# Create trace
trace = go.Histogram(x = data.values,
                     name = 'Ratings',
                     xbins = dict(start = 0,
                                  end = 50,
                                  size = 2))
# Create layout
layout = go.Layout(title = 'Distribution Of Number of Ratings Per Book (Clipped at 50)',
                   xaxis = dict(title = 'Number of Ratings Per Book'),
                   yaxis = dict(title = 'Count'),
                   bargap = 0.2)

# Create plot
fig = go.Figure(data=[trace], layout=layout)
plot(fig)

df.groupby('ISBN')['bookRating'].count().reset_index().sort_values('bookRating', ascending=False)[:10]

# Number of ratings per user
data = df.groupby('userID')['bookRating'].count().clip(upper=50)

# Create trace
trace = go.Histogram(x = data.values,
                     name = 'Ratings',
                     xbins = dict(start = 0,
                                  end = 50,
                                  size = 2))
# Create layout
layout = go.Layout(title = 'Distribution Of Number of Ratings Per User (Clipped at 50)',
                   xaxis = dict(title = 'Ratings Per User'),
                   yaxis = dict(title = 'Count'),
                   bargap = 0.2)

# Create plot
fig = go.Figure(data=[trace], layout=layout)
plot(fig)

df.groupby('userID')['bookRating'].count().reset_index().sort_values('bookRating', ascending=False)[:10]

min_book_ratings = 50
filter_books = df['ISBN'].value_counts() > min_book_ratings
filter_books = filter_books[filter_books].index.tolist()

min_user_ratings = 50
filter_users = df['userID'].value_counts() > min_user_ratings
filter_users = filter_users[filter_users].index.tolist()

df_new = df[(df['ISBN'].isin(filter_books)) & (df['userID'].isin(filter_users))]
print('The original data frame shape:\t{}'.format(df.shape))
print('The new data frame shape:\t{}'.format(df_new.shape))

reader = Reader(rating_scale=(0, 9))
data = Dataset.load_from_df(df_new[['userID', 'ISBN', 'bookRating']], reader)

benchmark = []
# Iterate over all algorithms
for algorithm in [SVD(), SVDpp(), NMF()]:
    # Perform cross validation
    results = cross_validate(algorithm, data, measures=['RMSE' , 'MAE' , 'MSE'], cv=5, verbose=False)

    # Get results & append algorithm name
    tmp = pd.DataFrame.from_dict(results).mean(axis=0)
    tmp = tmp.append(pd.Series([str(algorithm).split(' ')[0].split('.')[-1]], index=['Algorithm']))
    benchmark.append(tmp)

surprise_results = pd.DataFrame(benchmark).set_index('Algorithm').sort_values('test_rmse')

surprise_results

# Assuming df_new is your DataFrame containing the data
reader = Reader(rating_scale=(0, 9))
data = Dataset.load_from_df(df_new[['userID', 'ISBN', 'bookRating']], reader)

# Split the data into train and test sets
trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

# Instantiate the svd algorithm
svd = SVD()

# Train the svd algorithm on the training set
svd.fit(trainset)

# Generate predictions on the test set
predictions_svd = svd.test(testset)

# Extract the actual ratings and predicted ratings
actual_ratings = np.array([pred.r_ui for pred in predictions_svd])
predicted_ratings = np.array([pred.est for pred in predictions_svd])

cosine_svd = ((np.dot(actual_ratings,predicted_ratings)/(norm(actual_ratings)*norm(predicted_ratings)))+1)/2
print("Cosine Similarity:", cosine_svd)

# Instantiate the svdpp algorithm
svdpp = SVDpp()

# Train the svdpp algorithm on the training set
svdpp.fit(trainset)

# Generate predictions on the test set
predictions_svdpp = svdpp.test(testset)

# Extract the actual ratings and predicted ratings
actual_ratings = np.array([pred.r_ui for pred in predictions_svdpp])
predicted_ratings = np.array([pred.est for pred in predictions_svdpp])

cosine_svdpp = ((np.dot(actual_ratings,predicted_ratings)/(norm(actual_ratings)*norm(predicted_ratings)))+1)/2
print("Cosine Similarity:", cosine_svdpp)

# Instantiate the nmf algorithm
nmf = NMF()

# Train the nmf algorithm on the training set
nmf.fit(trainset)

# Generate predictions on the test set
predictions_nmf = nmf.test(testset)

# Extract the actual ratings and predicted ratings
actual_ratings = np.array([pred.r_ui for pred in predictions_nmf])
predicted_ratings = np.array([pred.est for pred in predictions_nmf])

cosine_nmf = ((np.dot(actual_ratings,predicted_ratings)/(norm(actual_ratings)*norm(predicted_ratings)))+1)/2
print("Cosine Similarity:", cosine_nmf)

plt.figure(figsize=(10, 7))

plt.subplot(1, 3, 1)
plt.pcolormesh([[cosine_svd]], cmap='coolwarm', vmin=0, vmax=1)
plt.text(0.5, 0.5, f"{cosine_svd:.3f}", color='black', fontsize=12,
         ha='center', va='center', fontweight='bold')
plt.title('SVD')


plt.subplot(1, 3, 2)
plt.pcolormesh([[cosine_svdpp]], cmap='coolwarm', vmin=0, vmax=1)
plt.text(0.5, 0.5, f"{cosine_svdpp:.3f}", color='black', fontsize=12,
         ha='center', va='center', fontweight='bold')
plt.title('SVDpp')

plt.subplot(1, 3, 3)
plt.pcolormesh([[cosine_nmf]], cmap='coolwarm', vmin=0, vmax=1)
plt.text(0.5, 0.5, f"{cosine_nmf:.3f}", color='black', fontsize=12,
         ha='center', va='center', fontweight='bold')
plt.title('NMF')

plt.colorbar(label='Similarity Colorbar')
plt.show()