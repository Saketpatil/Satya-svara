# Script to train CNN Model
import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam

# Check weather GPU is available
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

# Define paths
SPECTROGRAM_DIR = os.path.join(os.getcwd(), "data/spectrograms")
MODEL_SAVE_PATH = os.path.join(os.getcwd(), "models/cnn_model.keras")

# Hyperparameters
IMG_HEIGHT, IMG_WIDTH = 128, 128 
BATCH_SIZE = 32
EPOCHS = 100
LEARNING_RATE = 0.001

# Data augmentation and preprocessing
datagen = ImageDataGenerator(
    rescale=1.0/255,           
    validation_split=0.2      
)

train_generator = datagen.flow_from_directory(
    SPECTROGRAM_DIR,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='binary',       
    subset='training'
)

validation_generator = datagen.flow_from_directory(
    SPECTROGRAM_DIR,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    subset='validation'
)

# CNN model architecture
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')   
])

# Compile model
model.compile(optimizer=Adam(learning_rate=LEARNING_RATE),
              loss='binary_crossentropy',
              metrics=['accuracy'])

# Train model
history = model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // BATCH_SIZE,
    epochs=EPOCHS,
    validation_data=validation_generator,
    validation_steps=validation_generator.samples // BATCH_SIZE
)

# Save the model
model.save(MODEL_SAVE_PATH)
print(f"Model saved at {MODEL_SAVE_PATH}")
