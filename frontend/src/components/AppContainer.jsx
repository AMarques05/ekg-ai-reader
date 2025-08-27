import InfoContainer from './InfoContainer';
import GraphContainer from './GraphContainer';
import PastTests from './PastTests';


function AppContainer(){
    return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <div className={"h-[500px]  min-h-[400px] w-[700px] bg-gray-700 p-8 rounded-lg shadow-lg shadow-cyan-500/50 grid grid-cols-3 grid-rows-3 gap-1"}>
        <InfoContainer />
        <GraphContainer />
        <PastTests />
      </div>
    </div>
    )
}

export default AppContainer;