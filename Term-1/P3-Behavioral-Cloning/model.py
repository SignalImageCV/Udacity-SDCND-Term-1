### Import
import pickle
import numpy as np
import pandas as pd
import matplotlib.image as mpimg
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
import cv2
import math
import time
import h5py
import json

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D
from keras.optimizers import SGD, Adam, RMSprop
from keras.utils import np_utils


### Load data
# Read in images
images = os.listdir("Recorded Data/IMG/")
center_images = []

for idx, val in enumerate(images):
    # reading in an image
    if 'center' in images[idx]:
        image = mpimg.imread("Recorded Data/IMG/" + images[idx])
        center_images.append(image)

features = np.array(center_images)

# Read in CSV file
csv_loc = "Recorded Data/driving_log.csv"
df = pd.read_csv(csv_loc)
labels = df.iloc[:,3]
labels = labels.values.tolist()

labels = np.array(labels)

### Split data
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.15, random_state=432422)

### Normalize
def normalize_img(image):
	return cv2.normalize(image, None, alpha=-0.5, beta=0.5, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)

X_train = np.array([normalize_img(image) for image in X_train], dtype=np.float32)
X_test = np.array([normalize_img(image) for image in X_test], dtype=np.float32)

### Helper Functions
def data_generator(features, labels, batch_size):
	total_batch = int(len(features)/batch_size)

    features, labels = shuffle(features, labels)

    for i in range(total_batch):
        idx_l = i*batch_size
        idx_h = idx_l + batch_size

        batch_x = features[idx_l:idx_h]
        batch_y = labels[idx_l:idx_h]
		
		yield batch_x, batch_y
		
	
### Parameters
layer_1_depth = 32
filter_size = 5
num_classes = len(np.unique(y_train))
num_neurons = 128
epochs = 2
batch_size = 32
 
### Model
model = Sequential()
model.add(Convolution2D(layer_1_depth, filter_size, filter_size, border_mode = 'valid', input_shape = X_train.shape[1:]))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.5))
model.add(Flatten())
model.add(Dense(num_neurons))
model.add(Activation('relu'))
model.add(Dense(num_classes))

model.summary()

### Compile and Train
X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], X_train.shape[2],X_train.shape[3] )
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], X_test.shape[3], X_test.shape[3])

model.compile(loss='mse',
              optimizer=Adam(),
              metrics=['mean_absolute_error', 'accuracy'])


history = model.fit_generator(data_generator(X_train, y_train, batch_size), 
											samples_per_epoch=len(y_train), 
											nb_epoch = nb_epoch,
											verbose = 1,
											validation_data = (X_test, y_test))