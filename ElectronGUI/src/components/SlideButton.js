import React from "react";

function SlideButtonRange(props) {
  const { min, max, value, handleChange } = props;

  return (
    <div className="relative flex flex-row w-36 h-6 mx-2 items-center">
      <input
        type="range"
        min={min}
        max={max}
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
    this.props.callback(this.state.active ? this.state.value : -1);
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
          min={0}
          max={10}
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
            "hover:border-2 hover:rounded-none transition-all ease-linear " +
            (this.state.active
              ? "bg-green-400 hover:border-blue-600"
              : "bg-blue-600 hover:border-green-400")
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
