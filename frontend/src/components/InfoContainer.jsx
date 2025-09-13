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
                    
                    // Keep rows that have a time value - handle multiple time column names
                    const parsed = results.data.filter((row) => {
                        if (!row) return false;
                        const timeValue = row["Time(ms)"] ?? row["time"] ?? row["Time"] ?? row["TIME"];
                        return timeValue !== undefined && timeValue !== null;
                    });
                    console.log("Parsed rows with time column:", parsed.length); // Debug log

                    // Normalize to always provide 'Time(ms)' and 'value' keys for the chart
                    const normalized = parsed
                        .map((row) => {
                            // Get time value from various possible column names
                            const timeValue = row["Time(ms)"] ?? row["time"] ?? row["Time"] ?? row["TIME"];
                            // Get signal value from various possible column names
                            const v = row.value ?? row.Value ?? row["Lead_I"] ?? row["Lead II"] ?? row["Lead_II"] ?? row["Voltage"] ?? row["ECG"];
                            return {
                                "Time(ms)": typeof timeValue === 'string' ? Number(timeValue) : timeValue,
                                value: typeof v === 'string' ? Number(v) : v,
                            };
                        })
                        .filter((r) => {
                            return r["Time(ms)"] !== undefined && r["Time(ms)"] !== null && !Number.isNaN(r["Time(ms)"]) &&
                                   r.value !== undefined && r.value !== null && !Number.isNaN(r.value);
                        });

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
            const response = await fetch('http://localhost:5000/ekg/predict', {
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