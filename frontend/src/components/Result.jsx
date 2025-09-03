
import React, { useState, useEffect } from 'react';

function Result({prediction}){
    const [isShaking, setIsShaking] = useState(false);

    useEffect(() => {
        if (prediction) {
            setIsShaking(true);
            const timer = setTimeout(() => {
                setIsShaking(false);
            }, 500);
            
            return () => clearTimeout(timer);
        }
    }, [prediction]);

    const getResultColor = (prediction) => {
        switch(prediction?.toLowerCase()) {
            case 'normal':
                return 'border-green-500 bg-green-200 text-green-500';
            case 'afib':
                return 'border-red-500 bg-red-200 text-red-500';
            case 'pvc':
                return 'border-orange-500 bg-orange-200 text-orange-500';
            case 'bradycardia':
                return 'border-orange-500 bg-orange-200 text-orange-500';
            default:
                return 'border-gray-500 bg-gray-200 text-gray-500';
        }
    };

    function color() { return getResultColor(prediction)}

    return(
        <div className = {`h-2/5 w-full border-2 rounded flex justify-center items-center ${color()} ${isShaking ? 'animate-shake' : ''}`}>
            {prediction && <p className="text-center p-4 uppercase text-xl">{prediction}</p>}
        </div>
    )
}

export default Result;