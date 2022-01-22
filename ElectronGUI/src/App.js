import React from "react";
import SlideButton from "./components/SlideButton";
import LiveChart from "./components/LiveChart";

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
  maxFrames: 60,
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
      chartData: [],
      chartPoint: 0,
      arr: Array.from({ length: 5 * ChartConfig.maxFrames }, () =>
        Math.random() - 0.5
      ),
    };

    this.chartCallback = this.chartCallback.bind(this);
    this.moduleFunction = this.moduleFunction.bind(this);

    this.handleFade = this.handleFade.bind(this);
    this.handleDelay = this.handleDelay.bind(this);
    this.handleReverb = this.handleReverb.bind(this);
  }

  chartCallback() {
    return this.state.arr.shift();
  }

  handleFade = (value, active) => {
    this.setState({
      fade: value,
      useFade: active,
    });
    this.moduleFunction();
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

  moduleFunction = async () => {
    await paModule.createTSFN(this.moduleCallback);
  };

  moduleCallback = (...args) => {
    console.log(...args);
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
        <div className="relative flex-grow flex flex-col p-2">
          <div className="relative flex-grow h-1/2 flex flex-row border-2 border-gray-900 shadow-xl">
            <LiveChart callback={this.chartCallback} />
          </div>
        </div>
      </div>
    );
  }
}

export default App;
