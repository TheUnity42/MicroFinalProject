import { useState } from "react";
import SlideButton from "./components/SlideButton";

function App() {
  let config = useState({
    fade: -1,
    delay: -1,
    reverb: -1,
  });

  function fadeCallback(value) {
    config.setState({
      fade: value,
    });
  }

  function delayCallback(value) {
    config.setState({
      delay: value,
    });
  }

  function reverbcallback(value) {
    config.setState({
      reverb: value,
    });
  }
  
  return (
    <div className="flex flex-row w-screen h-screen bg-gray-800 divide-gray-900 divide-x">
      <div className="relative flex flex-col mx-1">
        <SlideButton text="Fade" callback={fadeCallback} />
        <SlideButton text="Delay" callback={delayCallback} />
        <SlideButton text="Reverb" callback={reverbcallback} />
      </div>
      <div className="relative flex flex-col m-1">
        <p>Fade: {config.fade}</p>
      </div>
    </div>
  );
}

export default App;
