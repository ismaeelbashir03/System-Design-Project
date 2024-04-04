import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

import os
from PIL import Image

def check_images(root_directory):
    # Walk through all directories and files in the root_directory
    for dirpath, dirnames, filenames in os.walk(root_directory):
        for filename in filenames:
            # Construct the full file path
            filepath = os.path.join(dirpath, filename)
            # Try to open the image
            try:
                with Image.open(filepath) as img:
                    # If successful, we can optionally do something with img
                    # For example, img.show() to open it with the default image viewer
                    img.verify()  # Verify that it's an image
            except (IOError, SyntaxError) as e:
                # Print the name of the file that caused an error
                print(f"Cannot open or the file is corrupt: {filepath}")
                # remove the file
                os.remove(filepath)

# Replace '/path/to/your/directory' with the actual path to your directory of pictures
root_directory_path = 'classification/data_processing/TrashBox-main/TrashBox_train_set'
check_images(root_directory_path)

# ===== SETTINGS =====
# DEVICE
device = "mps"

# HYPERPARAMETERS
BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 1e-3

# SEED
SEED = 42


# ===== LOADING THE DATA  =====

# DATASET FOLDER 
train_dir = 'classification/data_processing/TrashBox-main/TrashBox_train_set'

train_dataset = tf.keras.preprocessing.image_dataset_from_directory(train_dir, validation_split=0.1, subset="training", seed=42, batch_size=16, smart_resize=True)

classes = train_dataset.class_names
numClasses = len(train_dataset.class_names)
print(classes)

AUTOTUNE = tf.data.AUTOTUNE

train_dataset = train_dataset.prefetch(buffer_size=AUTOTUNE)



# ===== LOADING THE MODEL  =====

#INCEPTION V3 MODEL
"""
baseModel = tf.keras.applications.InceptionV3(input_shape=(256, 256,3),weights='imagenet', include_top=False, classes=numClasses)
for layer in baseModel.layers[:249]:
   layer.trainable = False
for layer in baseModel.layers[249:]:
   layer.trainable = True

last_output = data_augmentation (baseModel.output)
maxpooled_output = tf.keras.layers.Flatten()(last_output)
x = tf.keras.layers.Dense(1024, activation='relu')(maxpooled_output)
x = tf.keras.layers.Dropout(0.5)(x)
x = tf.keras.layers.Dense(numClasses, activation='softmax')(x)

model = tf.keras.Model(inputs=baseModel.input,outputs=x)"""

# RESNET152 MODEL

baseModel = tf.keras.applications.ResNet152(input_shape=(256, 256,3), weights='imagenet', include_top=False, classes=numClasses)
for layers in baseModel.layers:
  layers.trainable=False

last_output = baseModel.layers[-1].output
x = tf.keras.layers.Dropout(0.5) (last_output)
x = tf.keras.layers.Flatten()(x)
x = tf.keras.layers.Dense(128, activation = 'relu')(x)
x = tf.keras.layers.Dense(numClasses, activation='softmax')(x)

model = tf.keras.Model(inputs=baseModel.input,outputs=x)
model.summary()

# ===== TRAINING THE MODEL  =====

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001), loss=tf.keras.losses.SparseCategoricalCrossentropy(),metrics=['accuracy'])
epochs = 10
history = model.fit(train_dataset, epochs=epochs)

model.save('classification/waste_classifier_resnet.keras')