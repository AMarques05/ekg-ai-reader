import React, { useState, useEffect, useRef } from "react";
import Plot from "react-plotly.js";

export default function LiveEKG({ rawData }) {
  const [displayData, setDisplayData] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(2);
  const intervalRef = useRef(null);
  const indexRef = useRef(0);
  const WINDOW_SIZE = 1500;

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (rawData.length > 0) {
      stopAnimation();
      setDisplayData(rawData);
      indexRef.current = 0;
      console.log("Data loaded:", rawData.length, "points");
      console.log("Sample row:", rawData[0]);
    }
  }, [rawData]);

  const startAnimation = () => {
    if (rawData.length === 0 || isPlaying) return;
    
    setIsPlaying(true);
    indexRef.current = 0;
    setDisplayData([]);

    intervalRef.current = setInterval(() => {
      if (indexRef.current >= rawData.length) {
        stopAnimation();
        return;
      }

      const batchSize = speed; // Use speed as batch size
      const batch = [];
      
      for (let i = 0; i < batchSize && indexRef.current < rawData.length; i++) {
        const nextRow = rawData[indexRef.current];
        if (nextRow) {
          batch.push(nextRow);
        }
        indexRef.current += 1;
      }

      if (batch.length > 0) {
        setDisplayData((prev) => {
          const updated = [...prev, ...batch];
          return updated.length > WINDOW_SIZE ? updated.slice(-WINDOW_SIZE) : updated;
        });
      }
    }, 30);
  };

  const stopAnimation = () => {
    setIsPlaying(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const showAllData = () => {
    setIsPlaying(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setDisplayData(rawData); // Show all data at once
  };

  if (!rawData.length) {
    return (
      <div className="col-span-3 row-span-2 border-2 border-dashed border-gray-400 rounded-lg flex items-center justify-center bg-gray-800">
        <p className="text-gray-400">No data yet. Upload a file (CSV, JSON, Excel, or Text)!</p>
      </div>
    );
  }

  // Debug: Check if displayData has the right structure
  console.log("displayData length:", displayData.length);
  if (displayData.length > 0) {
    console.log("First displayData row:", displayData[0]);
  }

  return (
    <div className="col-span-3 row-span-2 border-2 border-dashed border-gray-400 rounded-lg bg-gray-800 p-3">
      {/* Controls */}
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-green-400 text-sm font-semibold">EKG Data Visualization</h3>
        <div className="flex items-center space-x-2">
          {/* Speed Control */}
          <div className="flex items-center space-x-1">
            <span className="text-xs text-gray-400">Speed:</span>
            <select
              value={speed}
              onChange={(e) => setSpeed(Number(e.target.value))}
              disabled={isPlaying}
              className="bg-gray-700 text-gray-300 text-xs px-1 py-0.5 rounded border border-gray-600"
            >
              <option value={1}>1x</option>
              <option value={2}>2x</option>
              <option value={5}>5x</option>
              <option value={10}>10x</option>
              <option value={20}>20x</option>
            </select>
          </div>
          
          {/* Play/Stop Controls */}
          <button
            onClick={startAnimation}
            disabled={isPlaying}
            className={`px-3 py-1 text-xs rounded transition-colors ${
              isPlaying 
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed' 
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            {isPlaying ? 'Playing...' : 'Play'}
          </button>
          <button
            onClick={stopAnimation}
            disabled={!isPlaying}
            className={`px-3 py-1 text-xs rounded transition-colors ${
              !isPlaying 
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed' 
                : 'bg-red-600 text-white hover:bg-red-700'
            }`}
          >
            Stop
          </button>
          <button
            onClick={showAllData}
            disabled={isPlaying}
            className={`px-3 py-1 text-xs rounded transition-colors ${
              isPlaying 
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed' 
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            Show All
          </button>
        </div>
      </div>

      {/* Chart */}
      <div className="h-full">
        <Plot
          data={[
            {
              x: displayData.map((row) => row["Time(ms)"]),
              y: displayData.map((row) => row["value"]),
              type: "scatter",
              mode: "lines",
              name: "Value",
              line: { color: "#10B981", width: 2 },
            },
          ]}
          layout={{
            title: {
              text: `EKG Data (${displayData.length}/${rawData.length} points)`,
              font: { color: "#10B981", size: 14 }
            },
            paper_bgcolor: "#374151",
            plot_bgcolor: "#1F2937",
            xaxis: {
              title: "Time (ms)",
              titlefont: { color: "#9CA3AF", size: 12 },
              tickfont: { color: "#9CA3AF", size: 10 },
              gridcolor: "#4B5563",
              gridwidth: 1,
              autorange: true, // Auto-adjust range for better zoom
              rangeslider: { visible: false }, // Remove range slider for more space
            },
            yaxis: { 
              title: "Value",
              titlefont: { color: "#9CA3AF", size: 12 },
              tickfont: { color: "#9CA3AF", size: 10 },
              gridcolor: "#4B5563",
              gridwidth: 1,
              autorange: true, // Auto-adjust range for better zoom
              fixedrange: false, // Allow zooming on Y-axis
            },
            legend: {
              font: { color: "#9CA3AF", size: 10 },
              bgcolor: "rgba(55, 65, 81, 0.8)"
            },
            margin: { t: 40, r: 15, b: 40, l: 45 }, // Optimized margins for more chart space
            autosize: true,
            showlegend: false,
            hovermode: 'closest',
            dragmode: 'zoom', // Default to zoom mode
            width: null, // Let it use full container width
            height: null, // Let it use full container height
          }}
          style={{ width: "100%", height: "calc(100% - 40px)" }}
          config={{
            displayModeBar: true, // Enable zoom controls
            modeBarButtonsToRemove: ['pan2d', 'select2d', 'lasso2d'],
            displaylogo: false,
            responsive: true,
            staticPlot: false,
            scrollZoom: true, // Enable scroll to zoom
            doubleClick: 'reset', // Double-click to reset zoom
          }}
          useResizeHandler={true}
        />
      </div>
    </div>
  );
}
