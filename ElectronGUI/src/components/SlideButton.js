import React from "react";

class SlideButton extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      active: false,
      };
      
      
  }

  onClick = () => {
    this.setState({
      active: !this.state.active,
    });
  };

  render() {
    return (
      <button
        onClick={this.onClick}
        className={
          "relative text-black w-36 h-12 m-2 justify-center text-center align-middle rounded-xl shadow-xl " +
          (this.state.active
            ? "bg-green-400 hover:border-blue-600 hover:border-2"
            : "bg-blue-600 hover:bg-green-400")
        }
      >
            {this.props.text}
      </button>
    );
  }
}

export default SlideButton;
