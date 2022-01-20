import React from "react";

function SlideButtonRange(props) {
  const {
    min,
    max,
    value,
    onChange,
  } = props;

  let printValue = value;

  const handleChange = (e) => {
    console.log(e.target.value);
    printValue = e.target.value;
  }



  return (
    <div className="relative flex flex-row w-36 h-6">
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={onChange}
        className="relative m-2"
      />
      <p>{value}</p>
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
  };

  onChange = (e) => {
    this.setState({
      value: e.target.value,
    });
  };

  render() {

    let slider = '';
    if (this.state.active) {
      slider = <SlideButtonRange min={0} max={10} value={this.state.value} onChange={this}/>;
    }

    return (
      <div className="relative flex flex-col">
        <button
          onClick={this.onClick}
          className={
            "relative text-black w-36 h-12 m-2 justify-center text-center align-middle rounded-xl shadow-xl " +
            "hover:border-2 hover:translate-x-4 transition-all ease-linear " +
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
