import Result from './Result';
import React, {useState} from 'react';
import Papa from 'papaparse';

function InfoContainer({ setData , onPredict}){

    const [file, setFile] = useState()
    const [prediction, setPrediction] = useState();

    const handleFileUpload = (e) => {
        const file = e.target.files[0];
        setFile(file);

        // Check file type and handle accordingly
        const fileName = file.name.toLowerCase();
        const fileExtension = fileName.split('.').pop();

        // For CSV files, use Papa Parse for preview (existing functionality)
        if (fileExtension === 'csv') {
            Papa.parse(file, {
                header: true,
                dynamicTyping: true,
                complete: (results) => {
                    console.log("Papa.parse results:", results); // Debug log
                    
                    const rows = results.data.filter(Boolean);

                    // Detect columns
                    const hasTime = rows.some((row) => (row["Time(ms)"] ?? row["time"] ?? row["Time"] ?? row["TIME"]) !== undefined);
                    const hasValue = rows.some((row) => (row.value ?? row.Value ?? row["Lead_I"] ?? row["Lead II"] ?? row["Lead_II"] ?? row["Voltage"] ?? row["ECG"]) !== undefined);

                    // Normalize to always provide 'Time(ms)' and 'value' keys for the chart
                    let normalized = [];
                    const fs = 250; // default sampling rate if time missing
                    if (hasValue) {
                        let idx = 0;
                        for (const row of rows) {
                            const t = hasTime ? (row["Time(ms)"] ?? row["time"] ?? row["Time"] ?? row["TIME"]) : (idx * 1000 / fs);
                            const v = row.value ?? row.Value ?? row["Lead_I"] ?? row["Lead II"] ?? row["Lead_II"] ?? row["Voltage"] ?? row["ECG"];
                            const timeNum = typeof t === 'string' ? Number(t) : t;
                            const valNum = typeof v === 'string' ? Number(v) : v;
                            if (timeNum !== undefined && timeNum !== null && !Number.isNaN(timeNum) &&
                                valNum !== undefined && valNum !== null && !Number.isNaN(valNum)) {
                                normalized.push({ "Time(ms)": timeNum, value: valNum });
                                idx += 1;
                            }
                        }
                    }

                    console.log("Normalized data:", normalized.length, "rows"); // Debug log
                    if (normalized.length > 0) {
                        console.log("First normalized row:", normalized[0]); // Debug log
                    }
                    setData(normalized);
                },
            });
        } else {
            // For non-CSV files (JSON, Excel, Text), show a placeholder message
            // The backend will handle the actual parsing when the file is submitted
            console.log(`File selected: ${fileName} (${fileExtension.toUpperCase()} format)`);
            console.log("File will be processed by backend when submitted for prediction.");
            
            // Set empty data for non-CSV files since we can't preview them easily
            // The chart will show a "Upload file to see preview" message
            setData([]);
        }
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
            const response = await fetch('http://localhost:5000/ekg/predict?use_hybrid=true&include_plot=true&threshold=0.00012', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            if (!response.ok) {
                console.log('Backend error:', data);
                return;
            }
            console.log('Result: ', data.result, 'MSE:', data.reconstruction_error);
            setPrediction(data.result);
            if (Array.isArray(data.plot)) {
                setData(data.plot);
            }
            onPredict(data.result);
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
                            accept=".csv,.json,.xlsx,.xls,.txt,.ekg"
                            className="hidden"
                            onChange={handleFileUpload}
                        />
                        Choose EKG File (CSV, JSON, Excel, Text)
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