import InfoContainer from './InfoContainer';
import PastTests from './PastTests';
import LiveEKG from './LiveEKG';
import React, {useState} from 'react';


function AppContainer(){
  const [rawData, setData] = useState([]);
  const [pastTests, setPastTests] = useState([]);

  function updateTests(prediction) {
        const newTest = {
            id: Date.now(),
            prediction: prediction,
            timestamp: new Date().toLocaleString()
        };
        setPastTests(prevTests => {
            const updatedTests = [newTest, ...prevTests];
            return updatedTests;
        });
  }

    return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <div className={"h-[600px] min-h-[500px] w-[1000px] bg-gray-700 p-8 rounded-lg shadow-lg shadow-cyan-500/50 grid grid-cols-4 grid-rows-3 gap-1"}>
        <InfoContainer setData = {setData} onPredict = {updateTests} />
        <LiveEKG rawData = {rawData} />
        <PastTests pastTests = {pastTests} />
      </div>
    </div>
    )
}

export default AppContainer;