import React, { useState, useEffect } from 'react';

function PastItem({prediction}){
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
                return 'border-green-500 bg-green-200 text-green-800';
            case 'afib':
                return 'border-red-500 bg-red-200 text-red-800';
            case 'pvc':
                return 'border-orange-500 bg-orange-200 text-orange-800';
            case 'bradycardia':
                return 'border-orange-500 bg-orange-200 text-orange-800';
            default:
                return 'border-gray-500 bg-gray-200 text-gray-800';
        }
    };

    function color() { return getResultColor(prediction)}

    return(
        <div className={`h-full w-full border-2 rounded flex flex-col justify-center items-center ${color()} ${isShaking ? 'animate-shake' : ''}`}>
            {prediction && (
                <>
                    <p className="text-center text-sm font-bold uppercase">{prediction}</p>
                </>
            )}
        </div>
    )
}

export default PastItem;