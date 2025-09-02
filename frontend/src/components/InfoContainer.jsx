import Result from './Result';
import React, {useState} from 'react';
import Papa from 'papaparse';

function InfoContainer({ setData }){

    const [file, setFile] = useState()
    const [prediction, setPrediction] = useState();

    const handleFileUpload = (e) => {
        const file = e.target.files[0];
        setFile(file);

        Papa.parse(file, {
        header: true,
        dynamicTyping: true,
        complete: (results) => {
            const parsed = results.data.filter((row) => row["Time(ms)"]);
            setData(parsed);
        },
        });
    };

    async function sendFile(){
        if(!file){
            console.log("No file Selected");
            return;
        }

        console.log("Sending Data To Backend...");

        const formData = new FormData();
        formData.append('file', file);

        try{
            const response = await fetch('http://localhost:5000/ekg/predict', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();
            console.log('Prediction: ', result.prediction);
            setPrediction(result.prediction);
        }catch(error) {
            console.log('Error: ', error);
        }
    }


    return(
        <div className = "flex flex-col justify-center items-center row-span-2 px-1 py-2 gap-y-2">
            <h1 className = "text-white font-mono text-2xl antialiased font-bold">EKG-AI-Reader</h1>
                <div className="w-full h-1/5 border-2 border-dashed border-blue-400 rounded-lg flex items-center justify-center bg-blue-50 hover:bg-blue-100 transition-colors duration-200">
                    <label htmlFor="file-input" className="cursor-pointer text-blue-600 font-medium">
                        <input 
                            id="file-input"
                            type="file" 
                            accept=".csv"
                            className="hidden"
                            onChange={handleFileUpload}
                        />
                        Choose CSV File
                    </label>
                </div>              
                <button className = "h-1/5 w-full border-2 rounded border-blue-600 bg-blue-300 text-blue-600 transition-all duration-300 ease-in-out hover:scale-105 hover:bg-blue-600 hover:text-white"
                    onClick={sendFile}>
                    Process
                </button>                
                <Result prediction={prediction} />
        </div>
    )
}

export default InfoContainer;