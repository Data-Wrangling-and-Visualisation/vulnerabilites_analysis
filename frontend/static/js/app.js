// Основной объект приложения
const App = {
    // Инициализация приложения
    init: function() {
        this.bindEvents();
        this.fetchData();
    },
    
    // Привязка событий
    bindEvents: function() {
        document.getElementById('apply-filters').addEventListener('click', () => this.applyFilters());
        document.getElementById('update-data').addEventListener('click', () => this.updateData());
    },
    
    // Загрузка данных
    fetchData: function(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        fetch(`/api/vulnerabilities?${queryString}`)
            .then(response => response.json())
            .then(data => {
                this.renderCharts(data.vulnerabilities);
                this.renderTable(data.vulnerabilities);
            })
            .catch(error => console.error('Error:', error));
    },
    
    // Обновление данных
    updateData: function() {
        const button = document.getElementById('update-data');
        button.disabled = true;
        button.textContent = 'Updating...';
        
        fetch('/api/update', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                this.fetchData();
            })
            .catch(error => console.error('Error:', error))
            .finally(() => {
                button.disabled = false;
                button.textContent = 'Update Database';
            });
    },
    
    // Применение фильтров
    applyFilters: function() {
        const severity = document.getElementById('severity-filter').value;
        const dateFrom = document.getElementById('date-from').value;
        const dateTo = document.getElementById('date-to').value;
        
        const params = {};
        if (severity !== 'all') params.severity = severity;
        if (dateFrom) params.date_from = dateFrom;
        if (dateTo) params.date_to = dateTo;
        
        this.fetchData(params);
    },
    
    // Отрисовка графиков
    renderCharts: function(data) {
        this.renderSeverityDistribution(data);
        this.renderCVSSOverTime(data);
        this.renderAttackVectorDistribution(data);
        this.renderTopCWE(data);
    },
    
    // График распределения по severity
    renderSeverityDistribution: function(data) {
        const severityCounts = {
            CRITICAL: 0,
            HIGH: 0,
            MEDIUM: 0,
            LOW: 0
        };
        
        data.forEach(vuln => {
            const severity = vuln.cvss_v3?.severity || vuln.cvss_v2?.severity || 'UNKNOWN';
            if (severityCounts[severity] !== undefined) {
                severityCounts[severity]++;
            }
        });
        
        const trace = {
            values: Object.values(severityCounts),
            labels: Object.keys(severityCounts),
            type: 'pie',
            marker: {
                colors: ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71']
            }
        };
        
        const layout = {
            title: 'Vulnerability Severity Distribution',
            height: 400,
            width: 500
        };
        
        Plotly.newPlot('severity-distribution', [trace], layout);
    },
    
    // График CVSS scores over time
    renderCVSSOverTime: function(data) {
        const monthlyData = {};
        
        data.forEach(vuln => {
            if (!vuln.published_date) return;
            
            const date = new Date(vuln.published_date);
            const monthYear = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;
            
            if (!monthlyData[monthYear]) {
                monthlyData[monthYear] = {
                    v2_scores: [],
                    v3_scores: []
                };
            }
            
            if (vuln.cvss_v2?.base_score) {
                monthlyData[monthYear].v2_scores.push(vuln.cvss_v2.base_score);
            }
            
            if (vuln.cvss_v3?.base_score) {
                monthlyData[monthYear].v3_scores.push(vuln.cvss_v3.base_score);
            }
        });
        
        const months = Object.keys(monthlyData).sort();
        const avgV2 = months.map(m => {
            const scores = monthlyData[m].v2_scores;
            return scores.length ? (scores.reduce((a, b) => a + b, 0) / scores.length : null;
        });
        
        const avgV3 = months.map(m => {
            const scores = monthlyData[m].v3_scores;
            return scores.length ? (scores.reduce((a, b) => a + b, 0) / scores.length : null;
        });
        
        const trace1 = {
            x: months,
            y: avgV2,
            name: 'CVSS v2',
            type: 'line',
            line: { color: '#3498db' }
        };
        
        const trace2 = {
            x: months,
            y: avgV3,
            name: 'CVSS v3',
            type: 'line',
            line: { color: '#9b59b6' }
        };
        
        const layout = {
            title: 'Average CVSS Scores Over Time',
            xaxis: { title: 'Month' },
            yaxis: { title: 'Average Score' },
            height: 400
        };
        
        Plotly.newPlot('cvss-scores-over-time', [trace1, trace2], layout);
    },
    
    // График распределения attack vectors
    renderAttackVectorDistribution: function(data) {
        const vectorCounts = {};
        
        data.forEach(vuln => {
            const vector = vuln.cvss_v3?.attack_vector || 'UNKNOWN';
            vectorCounts[vector] = (vectorCounts[vector] || 0) + 1;
        });
        
        const trace = {
            x: Object.keys(vectorCounts),
            y: Object.values(vectorCounts),
            type: 'bar',
            marker: {
                color: Object.keys(vectorCounts).map(
                    (_, i) => ['#3498db', '#2ecc71', '#e74c3c', '#f1c40f'][i % 4]
                )
            }
        };
        
        const layout = {
            title: 'Attack Vector Distribution (CVSS v3)',
            xaxis: { title: 'Attack Vector' },
            yaxis: { title: 'Count' },
            height: 400
        };
        
        Plotly.newPlot('attack-vector-distribution', [trace], layout);
    },
    
    // График топ CWE
    renderTopCWE: function(data) {
        const cweCounts = {};
        
        data.forEach(vuln => {
            if (!vuln.cwe) return;
            
            const cwes = vuln.cwe.split(', ').filter(cwe => cwe.startsWith('CWE-'));
            cwes.forEach(cwe => {
                cweCounts[cwe] = (cweCounts[cwe] || 0) + 1;
            });
        });
        
        const sortedCWE = Object.entries(cweCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);
        
        const trace = {
            x: sortedCWE.map(item => item[0]),
            y: sortedCWE.map(item => item[1]),
            type: 'bar',
            marker: { color: '#3498db' }
        };
        
        const layout = {
            title: 'Top 10 CWE Types',
            xaxis: { title: 'CWE ID' },
            yaxis: { title: 'Count' },
            height: 400
        };
        
        Plotly.newPlot('top-cwe', [trace], layout);
    },
    
    // Отрисовка таблицы
    renderTable: function(data) {
        const tableBody = document.querySelector('#vulnerabilities-table tbody');
        tableBody.innerHTML = '';
        
        data.slice(0, 50).forEach(vuln => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td><a href="https://nvd.nist.gov/vuln/detail/${vuln.cve_id}" target="_blank">${vuln.cve_id}</a></td>
                <td>${new Date(vuln.published_date).toLocaleDateString()}</td>
                <td>${vuln.cvss_v3?.base_score || vuln.cvss_v2?.base_score || 'N/A'}</td>
                <td class="severity-${vuln.cvss_v3?.severity || vuln.cvss_v2?.severity || ''}">
                    ${vuln.cvss_v3?.severity || vuln.cvss_v2?.severity || 'N/A'}
                </td>
                <td>${vuln.cvss_v3?.attack_vector || vuln.cvss_v2?.access_vector || 'N/A'}</td>
            `;
            
            tableBody.appendChild(row);
        });
    }
};

// Инициализация приложения после загрузки DOM
document.addEventListener('DOMContentLoaded', () => App.init());