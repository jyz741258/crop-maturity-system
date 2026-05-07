class CropCharts {
    constructor() {
        this.charts = {};
        this.defaultColors = {
            primary: '#2e7d32',
            secondary: '#43a047',
            light: '#81c784',
            accent: '#ffc107',
            warning: '#e67e22',
            danger: '#e53935',
            info: '#1e88e5',
            dark: '#424242'
        };
        this.maturityColors = {
            '幼嫩期': '#f39c12',
            '成熟期': '#27ae60',
            '过熟期': '#e67e22',
            '衰老期': '#95a5a6'
        };
    }

    initMaturityPieChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: data.labels.map(l => this.maturityColors[l] || this.defaultColors.primary),
                    borderColor: '#fff',
                    borderWidth: 3,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle',
                            font: { size: 13 }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        padding: 12,
                        titleFont: { size: 14 },
                        bodyFont: { size: 13 },
                        callbacks: {
                            label: (context) => {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.raw / total) * 100).toFixed(1);
                                return `${context.label}: ${context.raw} (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true
                }
            }
        });

        this.charts[containerId] = chart;
        return chart;
    }

    initTrendLineChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: '检测数量',
                    data: data.values,
                    borderColor: this.defaultColors.primary,
                    backgroundColor: 'rgba(46, 125, 50, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: this.defaultColors.primary,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        padding: 12,
                        titleFont: { size: 14 },
                        bodyFont: { size: 13 }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { font: { size: 11 }, color: '#666' }
                    },
                    y: {
                        grid: { color: '#eee' },
                        ticks: { font: { size: 11 }, color: '#666', beginAtZero: true }
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeOutQuart'
                }
            }
        });

        this.charts[containerId] = chart;
        return chart;
    }

    initRadarChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const chart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: '当前检测',
                    data: data.values,
                    backgroundColor: 'rgba(46, 125, 50, 0.2)',
                    borderColor: this.defaultColors.primary,
                    borderWidth: 2,
                    pointBackgroundColor: this.defaultColors.primary,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        padding: 12
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            font: { size: 10 },
                            color: '#666'
                        },
                        pointLabels: {
                            font: { size: 12 },
                            color: '#333'
                        },
                        grid: { color: '#ddd' },
                        angleLines: { color: '#ddd' }
                    }
                },
                animation: {
                    duration: 1200,
                    easing: 'easeOutQuart'
                }
            }
        });

        this.charts[containerId] = chart;
        return chart;
    }

    initQualityBarChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: '品质评分',
                    data: data.values,
                    backgroundColor: data.values.map(v => {
                        if (v >= 90) return this.defaultColors.primary;
                        if (v >= 70) return this.defaultColors.accent;
                        if (v >= 50) return this.defaultColors.warning;
                        return this.defaultColors.danger;
                    }),
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        padding: 12,
                        callbacks: {
                            label: (context) => `评分: ${context.raw}/100`
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { font: { size: 11 }, color: '#666' }
                    },
                    y: {
                        grid: { color: '#eee' },
                        ticks: { 
                            font: { size: 11 }, 
                            color: '#666',
                            beginAtZero: true,
                            max: 100
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeOutQuart'
                }
            }
        });

        this.charts[containerId] = chart;
        return chart;
    }

    initMaturityGauge(containerId, value, label) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const startAngle = 220;
        const endAngle = 320;
        const totalAngle = endAngle - startAngle;
        const percentage = value / 100;
        const currentAngle = startAngle + (totalAngle * percentage);

        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['进度', '背景'],
                datasets: [{
                    data: [percentage, 1 - percentage],
                    backgroundColor: [this.defaultColors.primary, '#e0e0e0'],
                    borderColor: '#fff',
                    borderWidth: 0,
                    hoverOffset: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '75%',
                rotation: (startAngle - 90) * (Math.PI / 180),
                circumference: totalAngle * (Math.PI / 180),
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            }
        });

        const centerX = ctx.width / 2;
        const centerY = ctx.height / 2;
        const drawCenterText = () => {
            const ctx2 = ctx.getContext('2d');
            ctx2.clearRect(0, 0, ctx.width, ctx.height);
            ctx2.fillStyle = '#333';
            ctx2.font = 'bold 32px Inter, sans-serif';
            ctx2.textAlign = 'center';
            ctx2.fillText(`${value}%`, centerX, centerY - 10);
            ctx2.font = '14px Inter, sans-serif';
            ctx2.fillStyle = '#666';
            ctx2.fillText(label, centerX, centerY + 20);
        };

        setTimeout(drawCenterText, 50);
        return chart;
    }

    updateChart(chartId, newData) {
        const chart = this.charts[chartId];
        if (!chart) return;

        chart.data.labels = newData.labels || chart.data.labels;
        chart.data.datasets[0].data = newData.values || chart.data.datasets[0].data;
        
        if (newData.colors) {
            chart.data.datasets[0].backgroundColor = newData.colors;
        }
        
        chart.update('none');
    }

    destroyChart(chartId) {
        const chart = this.charts[chartId];
        if (chart) {
            chart.destroy();
            delete this.charts[chartId];
        }
    }

    createMockData() {
        return {
            pieData: {
                labels: ['幼嫩期', '成熟期', '过熟期', '衰老期'],
                values: [45, 185, 68, 25]
            },
            trendData: {
                labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
                values: [120, 156, 134, 189, 167, 210, 195]
            },
            radarData: {
                labels: ['绿色占比', '纹理特征', '形态指标', '光谱特征', '综合评分'],
                values: [88, 76, 85, 82, 86]
            },
            barData: {
                labels: ['甜椒样本1', '甜椒样本2', '土豆样本1', '土豆样本2', '番茄样本1'],
                values: [95, 88, 92, 85, 98]
            },
            cropDistribution: {
                labels: ['甜椒', '土豆', '番茄'],
                values: [46, 5, 49],
                colors: ['#27ae60', '#f39c12', '#e74c3c']
            }
        };
    }
}

window.CropCharts = CropCharts;