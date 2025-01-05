"use client";

import { useState } from "react";
import axios, { AxiosResponse } from "axios";
import toast from "react-hot-toast";

const VideoDetection = () => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [isVisible, setIsVisible] = useState(false);
  const [result, setResult] = useState({
    cnn: {
      label: "",
      confidence: "",
    },
    rnn: {
      label: "",
      confidence: "",
    },
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setVideoFile(event.target.files[0] || null);
    }
  };

  const analyzeVideo = async () => {
    if (!videoFile) {
      toast.error("Please select a video file to analyze");
      return;
    }

    try {
      const response = axios.postForm("/api/analyze-video", {
        file: videoFile,
      });
      toast.promise(response, {
        loading: "Analyzing video...",
        success: (data: AxiosResponse) => {
          setResult(data.data.result);
          setIsVisible(true);
          return "Video analyzed successfully!";
        },
        error: "Error analyzing video",
      });
    } catch (error) {
      console.error("Error analyzing video:", error);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-base-300 text-base-content p-6">
      <div className="w-full max-w-2xl bg-base-100 rounded-lg shadow-lg p-6">
        <h1 className="text-4xl font-bold text-primary text-center">
          Video Detection
        </h1>
        <p className="mt-4 text-lg text-center">
          Upload a video file to detect whether it is real or fake.
        </p>
        <div className="mt-6 flex flex-col items-center gap-4">
          <input
            type="file"
            accept="video/*"
            onChange={handleFileChange}
            className="file-input file-input-bordered w-full max-w-md text-base-content"
          />
          <button
            className="btn btn-primary hover:btn-secondary mt-4"
            onClick={analyzeVideo}
          >
            Analyze Video Now
          </button>
        </div>
        {isVisible && (
          <div className="mt-6 p-4 bg-base-200 rounded-lg">
            <h2 className="text-2xl font-semibold text-center">
              Analysis Result
            </h2>
            <div className="mt-4 flex flex-col md:flex-row justify-around items-center gap-4">
              <div className="text-center">
                <h3 className="text-lg font-medium">CNN Prediction</h3>
                <button
                  className={`btn ${
                    result.cnn.label === "Real" ? "btn-success" : "btn-error"
                  }`}
                >
                  {result.cnn.label} ({result.cnn.confidence})
                </button>
              </div>
              <div className="text-center">
                <h3 className="text-lg font-medium">RNN Prediction</h3>
                <button
                  className={`btn ${
                    result.rnn.label === "Real" ? "btn-success" : "btn-error"
                  }`}
                >
                  {result.rnn.label} ({result.rnn.confidence})
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoDetection;
