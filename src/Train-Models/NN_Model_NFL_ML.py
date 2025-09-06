import sqlite3
import time

import numpy as np
import pandas as pd
import tensorflow as tf
from keras.callbacks import TensorBoard, EarlyStopping, ModelCheckpoint

current_time = str(time.time())

tensorboard = TensorBoard(log_dir='../../Logs/{}'.format(current_time))
earlyStopping = EarlyStopping(monitor='val_loss', patience=15, verbose=0, mode='min')
mcp_save = ModelCheckpoint('../../Models/Trained-Model-NFL-ML-' + current_time, save_best_only=True, monitor='val_loss', mode='min')

dataset = "nfl_dataset_2019-24"
con = sqlite3.connect("../../Data/NFLDataset.sqlite")
data = pd.read_sql_query(f"select * from \"{dataset}\"", con, index_col=None)
con.close()

scores = data['Score']
margin = data['Home-Team-Win']
columns_to_drop = ['Score', 'Home-Team-Win', 'TEAM_NAME', 'TEAM_NAME.1', 'Season', 'OU', 'OU-Cover']
existing_columns = [col for col in columns_to_drop if col in data.columns]
if 'Date' in data.columns:
    existing_columns.append('Date')
data.drop(existing_columns, axis=1, inplace=True)

data = data.values
data = data.astype(float)

x_train = tf.keras.utils.normalize(data, axis=1)
y_train = np.asarray(margin)

model = tf.keras.models.Sequential()
model.add(tf.keras.layers.Flatten())
model.add(tf.keras.layers.Dense(256, activation=tf.nn.relu6))
model.add(tf.keras.layers.Dropout(0.3))
model.add(tf.keras.layers.Dense(128, activation=tf.nn.relu6))
model.add(tf.keras.layers.Dropout(0.2))
model.add(tf.keras.layers.Dense(2, activation=tf.nn.softmax))

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(x_train, y_train, epochs=50, validation_split=0.1, batch_size=32, callbacks=[tensorboard, earlyStopping, mcp_save])

print('Done')
