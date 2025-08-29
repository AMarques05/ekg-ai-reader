
function Input() {
    return (
        <div className="w-full h-1/5 border-2 border-dashed border-blue-400 rounded-lg flex items-center justify-center bg-blue-50 hover:bg-blue-100 transition-colors duration-200">
            <label htmlFor="file-input" className="cursor-pointer text-blue-600 font-medium">
                <input 
                    id="file-input"
                    type="file" 
                    accept=".csv"
                    className="hidden"
                />
                Choose CSV File
            </label>
        </div>
    )
}

export default Input;