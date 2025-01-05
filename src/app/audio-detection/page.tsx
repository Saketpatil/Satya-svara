"use client";
import { useState } from "react";
import axios, { AxiosResponse } from "axios";
import toast from "react-hot-toast";

export default function Home() {
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [isVisibile, setIsVisible] = useState(false);
  const [result, setResult] = useState({
    cnn: {
      prediction: "",
      confidence: "",
    },
    rnn: {
      prediction: "",
      confidence: "",
    },
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setAudioFile(event.target.files[0] || null);
    }
  };

  const analyzeAudio = async () => {
    if (!audioFile) {
      toast.error("Please select an audio file to analyze");
      return;
    }
    try {
      const response = axios.postForm("/api/analyze-audio", {
        file: audioFile,
      });
      toast.promise(response, {
        loading: "Analyzing audio...",
        success: (data: AxiosResponse) => {
          setResult(data.data);
          setIsVisible(true);
          return "Audio analyzed successfully!";
        },
        error: "Error analyzing audio",
      });
    } catch (error) {
      console.error("Error analyzing audio:", error);
    }
  };

  return (
    <div className="hero bg-base-300 h-[57vh]">
      <div className="hero-content text-center w-[50vw]">
        <div className="w-full">
          <h1 className="text-5xl font-bold text-primary">
            Welcome to Staya-Svara
          </h1>
          <p className="py-6 text-base-content">
            Upload an audio file to detect fake audio using CNN and RNN models.
          </p>
          <div className="flex flex-col items-center gap-4">
            <input
              type="file"
              accept="audio/*"
              onChange={handleFileChange}
              className="file-input file-input-bordered w-full max-w-xs text-base-content"
            />
            <button
              className="btn btn-primary hover:btn-secondary mt-4"
              onClick={analyzeAudio}
            >
              Analyze Audio Now
            </button>
          </div>
          {isVisibile && (
            <div className="mt-4 text-base-content">
              <h2 className="text-xl font-semibold">Analysis Result:</h2>
              <p>
                CNN Prediction:
                {result.cnn.prediction}
                {result.cnn.confidence}
              </p>
              <p>
                RNN Prediction:
                {result.rnn.prediction}
                {result.rnn.confidence}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
