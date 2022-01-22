import { useState, useEffect, useRef } from "react";

const playButtonPath =
  "M66 44.1962C70 41.8868 70 36.1132 66 33.8038L9 0.894883C5 -1.41452 0 1.47223 0 6.09103L0 71.909C0 76.5278 5 79.4145 9 77.1051L66 44.1962Z";

function ControlBar(props) {
  const { playCallback, abortCallback } = props;

  const [play, setPlay] = useState(false);

  const didMount = useRef(false);

  useEffect(() => {
    if (didMount.current) {
      playCallback(play).then((res) => {
        if (res) {
          setPlay(false);
          abortCallback(false);
          if (res.code === 1) {
          } else if (res.code !== 0) {
            alert(res.message);
          }
        }
      });
    } else {
      didMount.current = true;
    }
  }, [play, setPlay, playCallback, abortCallback]);

  const handlePlay = () => {
    if (!play) {
      setPlay(true);
    } else {
      abortCallback(true);
    }
  };

  let playButton;

  if (!play) {
    playButton = (
      <svg
        className="w-4 h-4"
        viewBox="0 0 69 78"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path d={playButtonPath} fill="#10E030" />
      </svg>
    );
  } else {
    playButton = (
      <svg
        className="w-4 h-4"
        viewBox="0 0 57 80"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <rect width="20" height="80" rx="6" fill="#E0C040" />
        <rect x="37" width="20" height="80" rx="6" fill="#E0C040" />
      </svg>
    );
  }
  return (
    <div className="relative flex-grow flex-shrink flex mb-1 items-center justify-center">
      <button
        className="bg-gray-700 ring-2 ring-gray-900 ring-offset-gray-800 hover:ring-offset-2 p-1"
        onClick={handlePlay}
      >
        {playButton}
      </button>
    </div>
  );
}

export default ControlBar;
