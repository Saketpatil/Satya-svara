"use client";

export default function Home() {
  return (
    <div className="hero bg-base-300 h-[57vh]">
      <div className="hero-content text-center w-[50vw]">
        <div className="w-full">
          <h1 className="text-5xl font-bold text-primary">
            Welcome to Staya-Svara
          </h1>
          <p className="py-6 text-base-content">
            Your trusted solution for detecting fake audio. Upload audio files
            effortlessly and receive a detailed analysis powered by cutting-edge
            machine learning models. Stay informed, stay secure.
          </p>
          <a
            className="btn btn-primary hover:btn-secondary"
            href="/audio-detection"
          >
            Analyze Audio Now
          </a>
        </div>
      </div>
    </div>
  );
}
