import os
import sys
import io
import librosa
import librosa.display
import matplotlib
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from PIL import Image
import matplotlib.pyplot as plt

# Suppress TensorFlow warnings and logs
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
tf.get_logger().setLevel('ERROR')
matplotlib.use('Agg')

CNN_MODEL_PATH = os.path.join(os.getcwd(), 'python/models/model.keras')
RNN_MODEL_PATH = os.path.join(os.getcwd(), 'python/models/lstm_model.keras')
SPECTROGRAM_DIR = os.path.join(os.getcwd(), "python/spectrograms")
os.makedirs(SPECTROGRAM_DIR, exist_ok=True)

def load_models():
    try:
        cnn_model = load_model(CNN_MODEL_PATH)
        rnn_model = load_model(RNN_MODEL_PATH)
        return cnn_model, rnn_model
    except Exception as e:
        print(f"Error loading models: {e}")
        sys.exit(1)

def create_spectrogram(audio_path, output_path):
    try:
        y, sr = librosa.load(audio_path, sr=None)
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
        S_dB = librosa.power_to_db(S, ref=np.max)
        plt.figure(figsize=(10, 4))
        librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel')
        plt.axis('off')
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
        plt.close()
    except Exception as e:
        raise RuntimeError(f"Error creating spectrogram: {e}")

def extract_features(file_path):
    try:
        y, sr = librosa.load(file_path, sr=None)
        n_mfcc = 25
        sequence_length = 64
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
        
        if mfcc.shape[1] < sequence_length:
            padding = sequence_length - mfcc.shape[1]
            mfcc = np.pad(mfcc, ((0, 0), (0, padding)), mode='constant')
        elif mfcc.shape[1] > sequence_length:
            mfcc = mfcc[:, :sequence_length]
        
        return np.expand_dims(mfcc.T, axis=0) 
    except Exception as e:
        raise RuntimeError(f"Error extracting features: {e}")


def predict_audio(file_path, cnn_model, rnn_model):
    try:
        spectrogram_path = os.path.join(SPECTROGRAM_DIR, os.path.basename(file_path).replace('.wav', '.png'))
        create_spectrogram(file_path, spectrogram_path)

        image = Image.open(spectrogram_path).convert('RGB').resize((128, 128))
        image_array = np.expand_dims(np.array(image) / 255.0, axis=0)

        cnn_prediction = cnn_model.predict(image_array)
        cnn_label = 'Real' if cnn_prediction[0][0] > 0.5 else 'Fake'
        cnn_confidence = int(cnn_prediction[0][0] * 100)

        rnn_features = extract_features(file_path)
        rnn_prediction = rnn_model.predict(rnn_features)
        rnn_label = 'Real' if rnn_prediction[0][0] > 0.5 else 'Fake'
        rnn_confidence = int(rnn_prediction[0][0] * 100)

        os.remove(spectrogram_path)
        return {
            "cnn": {"label": cnn_label, "confidence": cnn_confidence},
            "rnn": {"label": rnn_label, "confidence": rnn_confidence},
        }
    except Exception as e:
        raise RuntimeError(f"Error during prediction: {e}")

def main(file_path):
    if not os.path.exists(file_path) or not file_path.lower().endswith('.wav'):
        raise ValueError("Invalid file. Please provide a valid .wav file.")
    cnn_model, rnn_model = load_models()
    predictions = predict_audio(file_path, cnn_model, rnn_model)
    return predictions

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: No audio file provided.")
        sys.exit(1)

    try:
        file_path = sys.argv[1]
        results = main(file_path)
        print(results)
    except Exception as e:
        print(f"Error: {e}")
