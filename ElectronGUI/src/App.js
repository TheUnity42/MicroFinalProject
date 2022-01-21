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

let chartData = {
  labels: [],
  data: [],
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
    };
  }

  componentDidMount() {
    this.chart = setInterval(() => this.chartTick(), ChartConfig.fps);
  }

  componentWillUnmount() {
    clearInterval(this.chart);
  }

  chartTick() {
    if (chartData.data.length > ChartConfig.maxFrames) {
      chartData.data.shift();
      chartData.labels.shift();
    }
  }

  handleFade = (value, active) => {
    this.setState({
      fade: value,
      useFade: active,
    });
    chartData.data.push(value);
    chartData.labels.push("");
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
        <LiveChart chartData={chartData} />
      </div>
    );
  }
}

// function App() {
//   let config = useState({
//     fade: -1,
//     delay: -1,
//     reverb: -1,
//   });

//   function fadeCallback(value) {
//     config.setState({
//       fade: value,
//     });
//     chartData.data.push(value);
//     console.log(value);
//   }

//   function delayCallback(value) {
//     config.setState({
//       delay: value,
//     });
//   }

//   function reverbcallback(value) {
//     config.setState({
//       reverb: value,
//     });
//   }

//   return (
//     <div className="flex flex-row w-screen h-screen bg-gray-800 divide-gray-900 divide-x">
//       <div className="relative flex flex-col mx-1">
//         <SlideButton text="Fade" callback={fadeCallback} />
//         <SlideButton text="Delay" callback={delayCallback} />
//         <SlideButton text="Reverb" callback={reverbcallback} />
//       </div>
//         <LiveChart chartData={chartData} />
//     </div>
//   );
// }

export default App;
