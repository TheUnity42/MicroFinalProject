import './App.css';
import SlideButton from './components/SlideButton';

function App() {

  return (
    <div className="flex flex-col w-screen h-screen bg-gray-800">
      <SlideButton text="Button 1"/>
      <SlideButton />
      <SlideButton />
    </div>
  );
}

export default App;
