import { Chart as ChartJS } from "chart.js/auto";
import { Chart } from "react-chartjs-2";
import { Line } from "react-chartjs-2";
import React from "react";

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
  },
  scales: {
    y: {
      min: -1,
      max: 1,
      color: "rgba(255, 255, 255, 1)",
    },

    // yAxes: {
    //   ticks: {
    //     color: "rgba(255, 255, 255, 1)",
    //     beginAtZero: false,
    //   },
    //   grid: {
    //     display: false,
    //     drawBorder: false,
    //   },
    // },

    xAxes: {
      ticks: {
        color: "rgba(255, 255, 255, 1)",
      },
      grid: {
        display: false,
        drawBorder: false,
      },
    },
  },
  layout: {},
};

const buildData = () => ({
  labels: "",
  datasets: [
    {
      label: [],
      data: [],
      backgroundColor: "rgba(255, 190, 0, 0.1)",
      borderColor: "rgba(242, 140, 40, 1)",
      pointBackgroundColor: "rgba(255, 255, 255, 1)",
      pointRadius: 0,
      fill: false,
      tension: 0.3,
    },
  ],
});

const timeFormat = (millis) => {
  const seconds = Math.floor(millis / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  return `${hours}:${minutes}:${seconds}`;
};

class LiveChart extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: buildData(),
      runTime: 0,
    };
    this.lineRef = React.createRef();
    this.updateFunc = this.updateFunc.bind(this);
  }

  componentDidMount() {
    this.updateCallback = setInterval(
      this.updateFunc,
      this.props.ChartConfig.fps
    );
  }

  componentWillUnmount() {
    clearInterval(this.updateCallback);
  }

  updateFunc = () => {
    const newVals = this.props.callback(); // fetch new value
    const timestamp = timeFormat(this.state.runTime); // get timestamp

    // update data
    if (newVals) {

      this.lineRef.data.datasets[0].data.push(...newVals);
      this.lineRef.data.labels.push(...newVals.keys());
      this.lineRef.update("none"); 
    }
    const diff = this.lineRef.data.datasets[0].data.length - this.props.ChartConfig.maxFrames;
    if (diff > 0) {
      this.lineRef.data.datasets[0].data.splice(0, diff);
      this.lineRef.data.labels.splice(0, diff);
      this.lineRef.update("none");
    }
  };

  render() {
    return (
      <div className="relative flex-grow w-full h-full bg-gray-700 items-center shadow-xl">
        <Line
          data={this.state.data}
          options={options}
          ref={(reference) => (this.lineRef = reference)}
        />
      </div>
    );
  }
}

export default LiveChart;
