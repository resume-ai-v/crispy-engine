import React from "react";

export default function AvatarPlayer({ videoUrl, audioUrl }) {
  if (!videoUrl && !audioUrl) return null;

  return (
    <div className="w-full mt-6 flex flex-col items-center">
      {videoUrl && (
        <div className="w-full max-w-xl mb-3">
          <video
            src={videoUrl}
            autoPlay
            controls
            className="rounded shadow w-full"
          >
            Sorry, your browser doesn't support embedded videos.
          </video>
        </div>
      )}

      {audioUrl && (
        <div className="w-full max-w-xl">
          <audio
            src={audioUrl}
            controls
            className="w-full"
          >
            Your browser does not support the audio element.
          </audio>
        </div>
      )}
    </div>
  );
}
