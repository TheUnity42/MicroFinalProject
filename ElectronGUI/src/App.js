import React from "react";
import SlideButton from "./components/SlideButton";
import LiveChart from "./components/LiveChart";

const backgroundColor = React.createContext("bg-gray-800");

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

let seed = 0;

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
  }

  chartCallback() {
    return this.state.arr.shift();
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
        <LiveChart callback={this.chartCallback} />
      </div>
    );
  }
}

export default App;
