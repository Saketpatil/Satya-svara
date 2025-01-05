import os
import sys
import io
import json
import librosa
import librosa.display
import matplotlib
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from PIL import Image
import matplotlib.pyplot as plt
import soundfile as sf
from moviepy import VideoFileClip

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
tf.get_logger().setLevel('ERROR')
matplotlib.use('Agg')

CNN_MODEL_PATH = os.path.join(os.getcwd(), 'python/models/model.keras')
RNN_MODEL_PATH = os.path.join(os.getcwd(), 'python/models/lstm_model.keras')
SPECTROGRAM_DIR = os.path.join(os.getcwd(), "python/spectrograms")
AUDIO_PATH = os.path.join(os.getcwd(), "python/audio")
os.makedirs(SPECTROGRAM_DIR, exist_ok=True)
os.makedirs(AUDIO_PATH, exist_ok=True)

def load_models():
    """
    Load CNN and RNN models from pre-defined paths.
    """
    try:
        cnn_model = load_model(CNN_MODEL_PATH)
        rnn_model = load_model(RNN_MODEL_PATH)
        return cnn_model, rnn_model
    except Exception as e:
        print(f"Error loading models: {e}")
        sys.exit(1)

def extract_audio_from_video(video_path):
    """
    Extracts the audio track from the video and saves it as a WAV file.
    """
    try:
        video = VideoFileClip(video_path)
        if not video.audio:
            raise RuntimeError("The video does not contain an audio track.")
        audio_output_path = os.path.join(AUDIO_PATH, "audio.wav")
        video.audio.write_audiofile(audio_output_path, codec="pcm_s16le")
        return audio_output_path
    except Exception as e:
        raise RuntimeError(f"Error extracting audio from video: {e}")

def create_spectrogram(audio_path, output_path):
    """
    Creates a spectrogram from the provided audio file and saves it as an image.
    """
    try:
        y, sr = librosa.load(audio_path, sr=None)
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
        S_dB = librosa.power_to_db(S, ref=np.max)
        plt.figure(figsize=(10, 4))
        librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel')
        plt.colorbar(format='%+2.0f dB')
        plt.tight_layout()
        plt.axis('off')
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
        plt.close()
    except Exception as e:
        raise RuntimeError(f"Error creating spectrogram: {e}")

def extract_features(file_path):
    """
    Extracts MFCC features from the audio file.
    """
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
    """
    Generates predictions for the provided audio file using CNN and RNN models.
    """
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

def slice_audio(audio_path, duration=2):
    """
    Slices the audio into smaller segments of the specified duration.
    """
    try:
        y, sr = librosa.load(audio_path, sr=None)
        total_duration = librosa.get_duration(y=y, sr=sr)
        slices = []

        for start in range(0, int(total_duration), duration):
            end = start + duration
            if end > total_duration:
                end = total_duration
            sliced_audio = y[int(start * sr):int(end * sr)]
            slices.append((sliced_audio, sr))
        return slices
    except Exception as e:
        raise RuntimeError(f"Error slicing audio: {e}")

def analyze_slices(audio_slices, cnn_model, rnn_model):
    """
    Processes each audio slice and accumulates predictions.
    """
    cnn_real_confidence = 0
    cnn_fake_confidence = 0
    rnn_real_confidence = 0
    rnn_fake_confidence = 0

    for idx, (audio_slice, sr) in enumerate(audio_slices):
        try:
            temp_audio_path = os.path.join(AUDIO_PATH, f"slice_{idx}.wav")
            sf.write(temp_audio_path, audio_slice, sr)
            predictions = predict_audio(temp_audio_path, cnn_model, rnn_model)
            
            cnn_real_confidence += predictions["cnn"]["confidence"] if predictions["cnn"]["label"] == "Real" else 0
            cnn_fake_confidence += predictions["cnn"]["confidence"] if predictions["cnn"]["label"] == "Fake" else 0
            rnn_real_confidence += predictions["rnn"]["confidence"] if predictions["rnn"]["label"] == "Real" else 0
            rnn_fake_confidence += predictions["rnn"]["confidence"] if predictions["rnn"]["label"] == "Fake" else 0

            os.remove(temp_audio_path)
        except Exception as e:
            print(f"Error processing slice {idx}: {e}")

    total_cnn_confidence = cnn_real_confidence + cnn_fake_confidence
    total_rnn_confidence = rnn_real_confidence + rnn_fake_confidence

    cnn_label = "Real" if cnn_real_confidence >= cnn_fake_confidence else "Fake"
    cnn_confidence = int(cnn_real_confidence / total_cnn_confidence * 100) if total_cnn_confidence > 0 else 0
    rnn_label = "Real" if rnn_real_confidence >= rnn_fake_confidence else "Fake"
    rnn_confidence = int(rnn_real_confidence / total_rnn_confidence * 100) if total_rnn_confidence > 0 else 0

    return {
        "cnn": {"label": cnn_label, "confidence": cnn_confidence},
        "rnn": {"label": rnn_label, "confidence": rnn_confidence},
    }

def main(file_path):
    """
    Orchestrates the audio processing pipeline.
    """
    cnn_model, rnn_model = load_models()
    audio_path = extract_audio_from_video(file_path)
    audio_slices = slice_audio(audio_path, duration=2)
    return analyze_slices(audio_slices, cnn_model, rnn_model)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: No video file provided.")
        sys.exit(1)

    try:
        file_path = sys.argv[1]
        results = main(file_path)
        print(json.dumps(results, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")
