import React from "react";

function SlideButtonRange(props) {
  const { min, max, step, value, handleChange } = props;

  return (
    <div className="relative flex flex-row w-36 h-6 mx-2 items-center">
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        defaultValue={value}
        onChange={handleChange}
        className="relative m-1 w-28 bg-blue-600"
      />
      <p className="relative m-1 text-green-400">{value}</p>
    </div>
  );
}

class SlideButton extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      active: false,
      value: 0,
    };
  }

  onClick = () => {
    this.setState({
      active: !this.state.active,
    });
    this.props.callback(this.state.value, this.state.active);
  };

  handleChange = (e) => {
    this.setState({
      value: e.target.value,
    });
    this.props.callback(e.target.value);
  };

  render() {
    let slider = "";
    if (this.state.active) {
      slider = (
        <SlideButtonRange
          min={this.props.config.min}
          max={this.props.config.max}
          step={this.props.config.step}
          value={this.state.value}
          handleChange={this.handleChange}
        />
      );
    }

    return (
      <div className="relative flex flex-col items-left">
        <button
          onClick={this.onClick}
          className={
            "relative text-black w-36 h-12 m-2 justify-center text-center align-middle rounded-xl shadow-xl " +
            "transition-all ease-linear ring-2 hover:ring-offset-2 ring-offset-gray-800 " +
            (this.state.active
              ? "bg-green-400 hover:ring-blue-600"
              : "bg-blue-600 hover:ring-green-400")
          }
        >
          {this.props.text}
        </button>
        {slider}
      </div>
    );
  }
}

export default SlideButton;
