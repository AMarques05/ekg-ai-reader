import React, { useState, useEffect, useRef } from "react";
import Plot from "react-plotly.js";

export default function LiveEKG({ rawData }) {
  const [displayData, setDisplayData] = useState([]);
  const [index, setIndex] = useState(0);
  const intervalRef = useRef(null);
  const WINDOW_SIZE = 500;

  useEffect(() => {
    if (rawData.length > 0) {
      clearInterval(intervalRef.current);
      setDisplayData([]);
      setIndex(0);

      intervalRef.current = setInterval(() => {
        setDisplayData((prev) => {
          const nextRow = rawData[index];
          if (!nextRow) {
            clearInterval(intervalRef.current);
            return prev;
          }
          const updated = [...prev, nextRow];
          if (updated.length > WINDOW_SIZE) updated.shift();
          return updated;
        });
        setIndex((prev) => prev + 1);
      }, 20);
    }
    return () => clearInterval(intervalRef.current);
  }, [rawData, index]);

  if (!rawData.length) {
    return (
      <div className="col-span-2 row-span-2 border-2 border-dashed border-gray-400 rounded-lg flex items-center justify-center bg-gray-800">
        <p className="text-gray-400">No data yet. Upload a CSV file!</p>
      </div>
    );
  }

  return (
    <div className="col-span-2 row-span-2 border-2 border-dashed border-gray-400 rounded-lg bg-gray-800 p-2">
      <Plot
        data={[
          {
            x: displayData.map((row) => row["Time(ms)"]),
            y: displayData.map((row) => row["Lead_I"]),
            type: "scatter",
            mode: "lines",
            name: "Lead I",
            line: { color: "#10B981" },
          },
          {
            x: displayData.map((row) => row["Time(ms)"]),
            y: displayData.map((row) => row["Lead_II"]),
            type: "scatter",
            mode: "lines",
            name: "Lead II",
            line: { color: "#34D399" },
          },
        ]}
        layout={{
          title: {
            text: "Live EKG Signal",
            font: { color: "#10B981" }
          },
          paper_bgcolor: "#374151",
          plot_bgcolor: "#1F2937",
          xaxis: {
            title: "Time (ms)",
            color: "#9CA3AF",
            gridcolor: "#4B5563",
            range: [
              displayData[0]?.["Time(ms)"] || 0,
              displayData[displayData.length - 1]?.["Time(ms)"] || 2000,
            ],
          },
          yaxis: { 
            title: "Voltage (mV)",
            color: "#9CA3AF",
            gridcolor: "#4B5563"
          },
          margin: { t: 40, r: 20, b: 40, l: 40 },
        }}
        style={{ width: "100%", height: "100%" }}
        config={{
          displayModeBar: false,
          responsive: true
        }}
      />
    </div>
  );
}
