import { Chart as ChartJS } from "chart.js/auto";
import { Chart } from "react-chartjs-2";
import { Line } from "react-chartjs-2";

const options = {
  responsive: true,
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
        // circular: true,
        // borderColor: "rgba(255, 255, 255, .2)",
        // color: "rgba(255, 255, 255, .2)",
        // borderDash: [5, 5],
      },
    },
  },
  layout: {},
};

const buildData = ({ chartData }) => ({
  labels: [ ...Array(chartData.length).fill("") ],
  datasets: [
    {
      label: chartData.keys(),
      data: chartData,
      backgroundColor: "rgba(255, 255, 255, 0.1)",
      borderColor: "rgba(255, 255, 255, 1)",
      pointBackgroundColor: "rgba(255, 255, 255, 1)",
      pointRadius: 0,
      fill: false,
      tension: 0.1,
    },
  ],
});

function LiveChart(props) {
  const data = buildData(props);
  console.log(data);
  return (
    <div className="relative flex-grow w-max h-1/2 bg-gray-800 text-white items-center">
      <Line data={data} options={options} />
    </div>
  );
}

export default LiveChart;
