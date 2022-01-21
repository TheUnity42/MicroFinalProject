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
  fps: 1000 / 60,
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
      arr: [],
    };

    this.brownianCallback = this.brownianCallback.bind(this);
  }

  componentDidMount() {
    this.chart = setInterval(() => this.chartTick(), ChartConfig.fps);
    this.test = setInterval(() => {
      seed++;

      paModule.runBrownianMotion(0, 5, 1, seed, this.brownianCallback);
    }, 2000);
  }

  componentWillUnmount() {
    clearInterval(this.chart);
    clearInterval(this.test);
  }

  componentDidUpdate() {
    console.log(this.state);
  }

  chartTick() {
    if (this.state.chartData.length > ChartConfig.maxFrames) {
      this.state.chartData.shift();
    }
  }

  brownianCallback(err, result) {
    if (result) {
      const out = Array.from(result);
      this.setState((state, props) => {
        return {
          chartData: state.chartData.concat(out),
        };
      });
    } else if (err) {
      console.log(err);
    }
  }

  handleFade = (value, active) => {
    this.setState({
      fade: value,
      useFade: active,
    });

    // paModule.runBrownianMotion(0, 15, 0.5, seed++, this.brownianCallback);
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
        <LiveChart chartData={this.state.chartData} />
      </div>
    );
  }
}

export default App;
