import React from "react";
import SlideButton from "./components/SlideButton";
import LiveChart from "./components/LiveChart";
import ControlBar from "./components/ControlBar";

const effectConfigs = {
  fade: {
    min: -1,
    max: 1,
    default: 0,
    step: 0.1,
  },
  delay: {
    min: 0,
    max: 10,
    default: 0,
    step: 0.5,
  },
  reverb: {
    min: 0,
    max: 5,
    default: 0,
    step: 0.2,
  },
};

const ChartConfig = {
  fps: 1000 / 30,
  maxFrames: 44100 / 10,
  sampleRate: 44100,
  samplesPerFrame: 44100 / 30,
  subSample: 4
};

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      useFade: false,
      useDelay: false,
      useReverb: false,
      fade: effectConfigs.fade.default,
      delay: effectConfigs.delay.default,
      reverb: effectConfigs.reverb.default,
      arr: [],
      abort: false
    };

    this.chartCallback = this.chartCallback.bind(this);
    this.handlePlay = this.handlePlay.bind(this);
    this.handleAbort = this.handleAbort.bind(this);

    this.handleFade = this.handleFade.bind(this);
    this.handleDelay = this.handleDelay.bind(this);
    this.handleReverb = this.handleReverb.bind(this);
  }

  chartCallback() {
    if (this.state.arr.length > 0) {
      return this.state.arr.splice(0, ChartConfig.samplesPerFrame);
    } else {
      return null;
    }
  }

  handleFade = (value, active) => {
    this.setState({
      fade: value,
      useFade: active,
    });
  };

  handleDelay = (value, active) => {
    this.setState({
      delay: value,
      useDelay: active,
    });
  };

  handleReverb = (value, active) => {
    this.setState({
      reverb: value,
      useReverb: active,
    });
  };

  moduleCallback = (frames, time, input, output) => {
    const inputArr = new Float32Array(input);
    const outputArr = new Float32Array(output);
    this.setState((prevState) => {
      return {
        arr: prevState.arr.concat(Array.from(inputArr)),
      }
    }, () => {
      console.log(this.state.arr.length);
    });
    return this.state.abort ? 1 : 0;
  };

  handlePlay = (play) => {
    if (play) {
      return window.effectslib.simplePlayback(this.moduleCallback, 0);
    } else {
      return Promise.resolve();
    }
  };

  handleAbort = (trigger) => {
    console.log("abort?: ", trigger);
    this.setState({
      abort: trigger
    });
  };

  render() {
    return (
      <div className="flex flex-row w-screen h-screen bg-gray-800 divide-gray-900 divide-x">
        <div className="relative flex flex-col mx-1">
          <SlideButton
            text="Fade"
            callback={this.handleFade}
            config={effectConfigs.fade}
          />
          <SlideButton
            text="Delay"
            callback={this.handleDelay}
            config={effectConfigs.delay}
          />
          <SlideButton
            text="Reverb"
            callback={this.handleReverb}
            config={effectConfigs.reverb}
          />
        </div>
        <div className="relative flex-grow flex-shrink flex flex-col p-1">
          <ControlBar playCallback={this.handlePlay} abortCallback={this.handleAbort}/>
          <div className="relative flex-grow flex-shrink flex flex-row border-2 border-gray-900 shadow-xl">
            <LiveChart callback={this.chartCallback} ChartConfig={ChartConfig} />
          </div>
        </div>
      </div>
    );
  }
}

export default App;
