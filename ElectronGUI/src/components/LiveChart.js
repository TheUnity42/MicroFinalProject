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
    yAxes: {
      ticks: {
        color: "rgba(255, 255, 255, 1)",
      },
      grid: {
        display: false,
        drawBorder: false,
      },
    },

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

const ChartConfig = {
  fps: 1000 / 30,
  maxFrames: 60,
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
  }

  componentDidMount() {
    this.updateCallback = setInterval(() => {
      const newVal = this.props.callback(); // fetch new value
      const timestamp = timeFormat(this.state.runTime); // get timestamp
      // update time
      this.setState((state, props) => {
        return {
          runTime: state.runTime + ChartConfig.fps,
        };
      });

      // update data
      if (newVal) {
        this.lineRef.data.datasets[0].data.push(newVal);
        this.lineRef.data.labels.push(timestamp);
        this.lineRef.update('none');
      }

      if (this.lineRef.data.datasets[0].data.length > ChartConfig.maxFrames) {
        this.lineRef.data.datasets[0].data.shift();
        this.lineRef.data.labels.shift();
        this.lineRef.update('none');
      }
    }, ChartConfig.fps);
  }

  componentWillUnmount() {
    clearInterval(this.updateCallback);
  }

  render() {
    return (
      <div className="relative flex-grow w-full h-full bg-gray-700 items-center shadow-xl">
      <Line data={this.state.data} options={options} ref={(reference) => this.lineRef = reference}/>
    </div>
    );
  }
}


// function LiveChart(props) {
//   const [data, setData] = React.useState(buildData());
//   // const data = buildData(props);
//   setData((prev) => {
//     return {
//       ...prev,
//       labels: prev.labels.concat(props.data.x),
//       datasets: prev.datasets.map((d) => ({
//         ...d,
//         data: d.data.concat(props.data.y),
//       })),
//     };
//   });
//   console.log(data);
//   return (
//     <div className="relative flex-grow w-max h-1/2 bg-gray-800 text-white items-center">
//       <Line data={data} options={options} />
//     </div>
//   );
// }

export default LiveChart;
