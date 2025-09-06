import sqlite3

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from tqdm import tqdm

dataset = "nfl_dataset_2019-24"
con = sqlite3.connect("../../Data/NFLDataset.sqlite")
data = pd.read_sql_query(f"select * from \"{dataset}\"", con, index_col=None)
con.close()

margin = data['Home-Team-Win']
data.drop(['Score', 'Home-Team-Win', 'TEAM_NAME', 'Date', 'TEAM_NAME.1', 'Date.1', 'OU-Cover', 'OU'],
          axis=1, inplace=True)

data = data.values

data = data.astype(float)
acc_results = []
for x in tqdm(range(100)):
    x_train, x_test, y_train, y_test = train_test_split(data, margin, test_size=.1)

    train = xgb.DMatrix(x_train, label=y_train)
    test = xgb.DMatrix(x_test, label=y_test)

    param = {
        'max_depth': 4,
        'eta': 0.02,
        'objective': 'multi:softprob',
        'num_class': 2,
        'subsample': 0.8,
        'colsample_bytree': 0.8
    }
    epochs = 500

    model = xgb.train(param, train, epochs)
    predictions = model.predict(test)
    y = []

    for z in predictions:
        y.append(np.argmax(z))

    acc = round(accuracy_score(y_test, y) * 100, 1)
    print(f"{acc}%")
    acc_results.append(acc)
    if acc == max(acc_results):
        model.save_model('../../Models/XGBoost_{}%_NFL_ML.json'.format(acc))
