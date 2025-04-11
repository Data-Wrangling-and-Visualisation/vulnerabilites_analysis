import React, { useEffect, useState } from 'react';
import * as d3 from 'd3';
import './App.css';

function App() {
  const [stats, setStats] = useState([]);
  const [vulnerabilities, setVulnerabilities] = useState([]);

  useEffect(() => {
    // Загрузка данных
    fetch('http://localhost:8000/api/stats')
      .then(res => res.json())
      .then(data => {
        setStats(data);
        drawChart(data);
      });

    fetch('http://localhost:8000/api/vulnerabilities?limit=50')
      .then(res => res.json())
      .then(setVulnerabilities);
  }, []);

  const drawChart = (data) => {
    const margin = {top: 20, right: 30, bottom: 40, left: 50};
    const width = 800 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // Очищаем предыдущий график
    d3.select("#chart").selectAll("*").remove();

    // Создаем SVG
    const svg = d3.select("#chart")
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Преобразуем данные
    const groupedData = d3.group(data, d => d.month);
    
    // Шкалы
    const x = d3.scaleBand()
      .domain([...groupedData.keys()])
      .range([0, width])
      .padding(0.2);

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.count) * 1.1])
      .range([height, 0]);

    // Оси
    svg.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x).tickFormat(d3.timeFormat("%b %Y")));

    svg.append("g")
      .call(d3.axisLeft(y));

    // Столбцы
    const severityColors = {
      "CRITICAL": "#ff0000",
      "HIGH": "#ff6600",
      "MEDIUM": "#ffcc00",
      "LOW": "#00cc00"
    };

    svg.selectAll(".bar")
      .data(data)
      .enter()
      .append("rect")
      .attr("class", "bar")
      .attr("x", d => x(d.month))
      .attr("y", d => y(d.count))
      .attr("width", x.bandwidth())
      .attr("height", d => height - y(d.count))
      .attr("fill", d => severityColors[d.severity] || "#999");
  };

  return (
    <div className="App">
      <h1>Vulnerability Dashboard</h1>
      <div id="chart"></div>
      
      <h2>Recent Vulnerabilities</h2>
      <table>
        <thead>
          <tr>
            <th>CVE ID</th>
            <th>Published</th>
            <th>Severity</th>
            <th>CVSS v3 Score</th>
          </tr>
        </thead>
        <tbody>
          {vulnerabilities.map(v => (
            <tr key={v.cve_id}>
              <td>{v.cve_id}</td>
              <td>{new Date(v.published_date).toLocaleDateString()}</td>
              <td style={{color: 
                v.cvss_v3_severity === 'CRITICAL' ? '#ff0000' :
                v.cvss_v3_severity === 'HIGH' ? '#ff6600' :
                v.cvss_v3_severity === 'MEDIUM' ? '#ffcc00' : '#00cc00'
              }}>
                {v.cvss_v3_severity}
              </td>
              <td>{v.cvss_v3_base_score}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;