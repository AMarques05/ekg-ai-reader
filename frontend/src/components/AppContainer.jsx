import InfoContainer from './InfoContainer';
import PastTests from './PastTests';
import LiveEKG from './LiveEKG';
import React, {useState} from 'react';


function AppContainer(){
  const [rawData, setData] = useState([]);

    return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <div className={"h-[500px]  min-h-[400px] w-[700px] bg-gray-700 p-8 rounded-lg shadow-lg shadow-cyan-500/50 grid grid-cols-3 grid-rows-3 gap-1"}>
        <InfoContainer setData = {setData} />
        <LiveEKG rawData = {rawData} />
        <PastTests />
      </div>
    </div>
    )
}

export default AppContainer;