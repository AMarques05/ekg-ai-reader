import PastItem from './PastItem';

function PastTests({pastTests}){
    
    return (
        <div className="flex flex-row items-center col-span-4 border-2 border-dashed border-gray-400 rounded-lg p-2 gap-2 overflow-x-auto">
            {pastTests && pastTests.length > 0 ? (
                pastTests.map((test) => (
                    <div key={test.id} className="flex-shrink-0 w-32 h-32">
                        <PastItem 
                            prediction={test.prediction}
                        />
                    </div>
                ))
            ) : (
                <p className="text-gray-400 text-center w-full">No past tests yet</p>
            )}
        </div>
    )
}

export default PastTests;