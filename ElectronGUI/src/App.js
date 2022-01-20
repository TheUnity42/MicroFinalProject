import SlideButton from "./components/SlideButton";

function App() {
  return (
    <div className="flex flex-col w-screen h-screen bg-gray-800">
      <SlideButton text="Fade" />
      <SlideButton text="Delay" />
      <SlideButton text="Reverb" />
    </div>
  );
}

export default App;
