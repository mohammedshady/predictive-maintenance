import React, { useState, useEffect } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

const RADIAN = Math.PI / 180;
const cx = 150;
const cy = 200;
const iR = 50;
const oR = 100;

const needle = (value, data, cx, cy, iR, oR, color) => {
  let total = 0;
  data.forEach((v) => {
    total += v.value;
  });
  const ang = 180.0 * (1 - value / total);
  const length = (iR + 2 * oR) / 3;
  const sin = Math.sin(-RADIAN * ang);
  const cos = Math.cos(-RADIAN * ang);
  const r = 5;
  const x0 = cx + 5;
  const y0 = cy + 5;
  const xba = x0 + r * sin;
  const yba = y0 - r * cos;
  const xbb = x0 - r * sin;
  const ybb = y0 + r * cos;
  const xp = x0 + length * cos;
  const yp = y0 + length * sin;

  return [
    <circle key="circle" cx={x0} cy={y0} r={r} fill={color} stroke="none" />,
    <path
      key="path"
      d={`M${xba} ${yba}L${xbb} ${ybb} L${xp} ${yp} L${xba} ${yba}`}
      stroke="none"
      fill={color}
    />,
  ];
};

const PieChartComponent = ({ logs }) => {
  const failureCount = logs.filter((log) => log.predictedFailure).length;
  const totalLogs = logs.length;
  const failureRate = totalLogs ? (failureCount / totalLogs) * 100 : 0;

  const dynamicData = [
    { name: "Normal", value: 80, color: "#00ff00" },
    { name: "Failure", value: 20, color: "#ff0000" },
  ];

  const [animatedValue, setAnimatedValue] = useState(0); // State for needle animation

  useEffect(() => {
    let animationFrame;
    const increment = () => {
      setAnimatedValue((prev) => {
        if (prev < failureRate) {
          return Math.min(prev + 1, failureRate); // Increment by 1 until the failureRate is reached
        } else {
          cancelAnimationFrame(animationFrame); // Stop the animation once the target is reached
          return prev;
        }
      });
      animationFrame = requestAnimationFrame(increment);
    };
    increment();
    return () => cancelAnimationFrame(animationFrame); // Clean up
  }, [failureRate]);

  return (
    <div className="pie-chart-needle-wrapper">
      <PieChart width={300} height={300}>
        <Pie
          dataKey="value"
          startAngle={180}
          endAngle={0}
          data={dynamicData}
          cx={cx}
          cy={cy}
          innerRadius={iR}
          outerRadius={oR}
          fill="#8884d8"
          stroke="none"
        >
          {dynamicData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        {needle(animatedValue, dynamicData, cx, cy, iR, oR, "#d0d000")}
      </PieChart>
      <h1 className="pie-chart-needle-legend">{100 - failureCount}%</h1>
    </div>
  );
};

export default PieChartComponent;
