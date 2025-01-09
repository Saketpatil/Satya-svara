# Script to generate spectrogram
import os
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

DATA_DIR = os.path.join(os.getcwd(), "data/audio")
OUTPUT_DIR = os.path.join(os.getcwd(), "data/spectrograms")

os.makedirs(os.path.join(OUTPUT_DIR, 'real'), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, 'fake'), exist_ok=True)

def create_spectrogram(audio_path, output_path):
    y, sr = librosa.load(audio_path, sr=None)
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)   
    S_dB = librosa.power_to_db(S, ref=np.max)

    plt.figure(figsize=(10, 4))
    librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Mel-frequency spectrogram')
    plt.tight_layout()
    plt.axis('off') 

    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    plt.close()

def process_audio_files(audio_dir, output_dir):
    for filename in os.listdir(audio_dir):
        if filename.endswith(".wav"):  
            audio_path = os.path.join(audio_dir, filename)
            output_path = os.path.join(output_dir, filename.replace('.wav', '.png'))
            create_spectrogram(audio_path, output_path)
            print(f"Saved spectrogram for {filename} to {output_path}")

if __name__ == "__main__":
    process_audio_files(os.path.join(DATA_DIR, "real"), os.path.join(OUTPUT_DIR, "real"))
    process_audio_files(os.path.join(DATA_DIR, "fake"), os.path.join(OUTPUT_DIR, "fake"))
