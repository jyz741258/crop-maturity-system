class CropCharts {
    constructor() {
        this.charts = {};
        this.colors = {
            primary: '#2e7d32',
            primaryLight: '#43a047',
            secondary: '#81c784',
            accent: '#ffc107',
            danger: '#e53935',
            warning: '#f39c12',
            info: '#2196f3',
            success: '#4caf50',
            immature: '#8bc34a',
            growing: '#ffc107',
            mature: '#4caf50',
            overripe: '#e53935'
        };
    }

    initMaturityPieChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const chartData = data || {
            labels: ['幼嫩期', '生长期', '成熟期', '过熟期'],
            values: [15, 25, 45, 15]
        };

        this.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: chartData.labels,
                datasets: [{
                    data: chartData.values,
                    backgroundColor: [this.colors.immature, this.colors.growing, this.colors.mature, this.colors.overripe],
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle',
                            font: { size: 12 }
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
                }
            }
        });
    }

    initTrendLineChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const chartData = data || {
            labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
            mature: [150, 180, 165, 200, 190, 220, 210],
            growing: [80, 75, 90, 85, 95, 88, 92]
        };

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: '成熟作物',
                    data: chartData.mature,
                    borderColor: this.colors.mature,
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointHoverRadius: 8,
                    pointBackgroundColor: this.colors.mature
                }, {
                    label: '生长期作物',
                    data: chartData.growing,
                    borderColor: this.colors.growing,
                    backgroundColor: 'rgba(255, 193, 7, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointHoverRadius: 8,
                    pointBackgroundColor: this.colors.growing
                }]
            },
            options: {
                responsive: true,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: { size: 12 }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        padding: 12,
                        callbacks: {
                            label: (context) => `${context.dataset.label}: ${context.raw}株`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0,0,0,0.05)' },
                        ticks: { font: { size: 11 }, stepSize: 50 }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { font: { size: 11 } }
                    }
                }
            }
        });
    }

    initAreaChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const chartData = data || {
            labels: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
            matureRate: [65, 68, 72, 78, 82, 85, 88, 85, 80, 75, 70, 68],
            avgQuality: [72, 75, 78, 80, 82, 84, 86, 85, 83, 80, 77, 74]
        };

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: '成熟率(%)',
                    data: chartData.matureRate,
                    borderColor: this.colors.primary,
                    backgroundColor: (context) => {
                        const ctx = context.chart.ctx;
                        const gradient = ctx.createLinearGradient(0, 0, 0, 200);
                        gradient.addColorStop(0, 'rgba(46, 125, 50, 0.3)');
                        gradient.addColorStop(1, 'rgba(46, 125, 50, 0)');
                        return gradient;
                    },
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6
                }, {
                    label: '平均品质分',
                    data: chartData.avgQuality,
                    borderColor: this.colors.accent,
                    backgroundColor: (context) => {
                        const ctx = context.chart.ctx;
                        const gradient = ctx.createLinearGradient(0, 0, 0, 200);
                        gradient.addColorStop(0, 'rgba(255, 193, 7, 0.2)');
                        gradient.addColorStop(1, 'rgba(255, 193, 7, 0)');
                        return gradient;
                    },
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                interaction: { mode: 'index' },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { padding: 20, usePointStyle: true }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        padding: 12
                    }
                },
                scales: {
                    y: {
                        min: 50,
                        max: 100,
                        grid: { color: 'rgba(0,0,0,0.05)' }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    initScatterChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const chartData = data || this.generateScatterData();

        this.charts[canvasId] = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: '幼嫩期',
                    data: chartData.immature,
                    backgroundColor: this.colors.immature,
                    pointRadius: 6,
                    pointHoverRadius: 10
                }, {
                    label: '生长期',
                    data: chartData.growing,
                    backgroundColor: this.colors.growing,
                    pointRadius: 6,
                    pointHoverRadius: 10
                }, {
                    label: '成熟期',
                    data: chartData.mature,
                    backgroundColor: this.colors.mature,
                    pointRadius: 6,
                    pointHoverRadius: 10
                }, {
                    label: '过熟期',
                    data: chartData.overripe,
                    backgroundColor: this.colors.overripe,
                    pointRadius: 6,
                    pointHoverRadius: 10
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { padding: 15, usePointStyle: true }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        padding: 12,
                        callbacks: {
                            label: (context) => {
                                const data = context.raw;
                                return `绿色占比: ${data.x.toFixed(1)}% | 纹理得分: ${data.y.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: '绿色占比(%)' },
                        min: 0,
                        max: 100,
                        grid: { color: 'rgba(0,0,0,0.05)' }
                    },
                    y: {
                        title: { display: true, text: '纹理得分' },
                        min: 0,
                        max: 1,
                        grid: { color: 'rgba(0,0,0,0.05)' }
                    }
                }
            }
        });
    }

    generateScatterData() {
        return {
            immature: Array(15).fill(null).map(() => ({
                x: 70 + Math.random() * 25,
                y: 0.2 + Math.random() * 0.2
            })),
            growing: Array(20).fill(null).map(() => ({
                x: 40 + Math.random() * 30,
                y: 0.3 + Math.random() * 0.3
            })),
            mature: Array(25).fill(null).map(() => ({
                x: 20 + Math.random() * 30,
                y: 0.5 + Math.random() * 0.3
            })),
            overripe: Array(10).fill(null).map(() => ({
                x: 5 + Math.random() * 20,
                y: 0.3 + Math.random() * 0.4
            }))
        };
    }

    initHeatmapChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const chartData = data || this.generateHeatmapData();
        const labels = chartData.labels || ['地块A', '地块B', '地块C', '地块D', '地块E'];
        const months = chartData.months || ['1月', '2月', '3月', '4月', '5月', '6月'];
        const heatmapData = chartData.data || [
            [65, 70, 75, 80, 82, 78],
            [55, 60, 68, 72, 75, 70],
            [70, 72, 78, 85, 88, 82],
            [60, 65, 72, 78, 80, 76],
            [58, 62, 68, 74, 78, 73]
        ];

        const flattenedData = [];
        heatmapData.forEach((row, i) => {
            row.forEach((value, j) => {
                flattenedData.push({ x: j, y: i, v: value });
            });
        });

        this.charts[canvasId] = new Chart(ctx, {
            type: 'matrix',
            data: {
                labels: labels,
                datasets: [{
                    label: '成熟率',
                    data: flattenedData,
                    backgroundColor: (context) => {
                        const value = context.raw.v;
                        if (value >= 80) return 'rgba(76, 175, 80, 0.8)';
                        if (value >= 70) return 'rgba(255, 193, 7, 0.7)';
                        if (value >= 60) return 'rgba(243, 156, 18, 0.6)';
                        return 'rgba(229, 57, 53, 0.5)';
                    },
                    borderColor: 'rgba(255,255,255,0.3)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        padding: 12,
                        callbacks: {
                            title: (context) => `${labels[context[0].raw.y]} - ${months[context[0].raw.x]}`,
                            label: (context) => `成熟率: ${context.raw.v}%`
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        min: 0,
                        max: months.length - 1,
                        ticks: {
                            stepSize: 1,
                            callback: (value) => months[value]
                        },
                        grid: { display: false },
                        title: { display: true, text: '月份' }
                    },
                    y: {
                        type: 'linear',
                        min: 0,
                        max: labels.length - 1,
                        ticks: {
                            stepSize: 1,
                            callback: (value) => labels[value]
                        },
                        grid: { display: false },
                        title: { display: true, text: '地块' }
                    }
                }
            }
        });
    }

    generateHeatmapData() {
        return {
            labels: ['地块A', '地块B', '地块C', '地块D', '地块E'],
            months: ['1月', '2月', '3月', '4月', '5月', '6月'],
            data: [
                [65, 70, 75, 80, 82, 78],
                [55, 60, 68, 72, 75, 70],
                [70, 72, 78, 85, 88, 82],
                [60, 65, 72, 78, 80, 76],
                [58, 62, 68, 74, 78, 73]
            ]
        };
    }

    initQualityBarChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const chartData = data || {
            labels: ['茶叶', '烟叶', '桑叶', '生菜', '菠菜', '芹菜'],
            scores: [85, 78, 88, 82, 76, 80]
        };

        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: '品质评分',
                    data: chartData.scores,
                    backgroundColor: chartData.scores.map(score => {
                        if (score >= 85) return this.colors.mature;
                        if (score >= 75) return this.colors.growing;
                        return this.colors.warning;
                    }),
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y',
                plugins: {
                    legend: { display: false },
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
                        min: 0,
                        max: 100,
                        grid: { color: 'rgba(0,0,0,0.05)' },
                        title: { display: true, text: '品质评分' }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { font: { size: 12 } }
                    }
                }
            }
        });
    }

    initRadarChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const chartData = data || {
            labels: ['绿色占比', '纹理特征', '形态指标', '光谱特征', '综合评分'],
            values: [82, 75, 88, 78, 85]
        };

        this.charts[canvasId] = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: '检测结果',
                    data: chartData.values,
                    backgroundColor: 'rgba(46, 125, 50, 0.2)',
                    borderColor: this.colors.primary,
                    borderWidth: 2,
                    pointBackgroundColor: this.colors.primary,
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: this.colors.primary
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { stepSize: 20, font: { size: 10 } },
                        grid: { color: 'rgba(0,0,0,0.1)' },
                        angleLines: { color: 'rgba(0,0,0,0.1)' },
                        pointLabels: { font: { size: 11 } }
                    }
                }
            }
        });
    }

    initGaugeChart(canvasId, value, label) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const gaugeValue = value || 78;
        const gaugeLabel = label || '成熟率';
        const normalizedValue = gaugeValue / 100;
        const startAngle = 135;
        const endAngle = 405;

        this.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [normalizedValue, 1 - normalizedValue],
                    backgroundColor: [
                        this._getGaugeColor(gaugeValue),
                        'rgba(0,0,0,0.05)'
                    ],
                    borderWidth: 0,
                    cutout: '75%'
                }]
            },
            options: {
                responsive: true,
                rotation: startAngle,
                circumference: endAngle - startAngle,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                },
                animation: {
                    animateRotate: true,
                    duration: 1500,
                    easing: 'easeOutQuart'
                }
            }
        });

        this._drawGaugeCenter(ctx, gaugeValue, gaugeLabel);
    }

    _getGaugeColor(value) {
        if (value >= 80) return this.colors.mature;
        if (value >= 60) return this.colors.growing;
        return this.colors.danger;
    }

    _drawGaugeCenter(ctx, value, label) {
        setTimeout(() => {
            const centerX = ctx.width / 2;
            const centerY = ctx.height / 2;
            
            const ctx2 = ctx.getContext('2d');
            ctx2.fillStyle = '#333';
            ctx2.font = 'bold 24px Inter, sans-serif';
            ctx2.textAlign = 'center';
            ctx2.textBaseline = 'bottom';
            ctx2.fillText(`${value}%`, centerX, centerY + 5);
            
            ctx2.fillStyle = '#666';
            ctx2.font = '12px Inter, sans-serif';
            ctx2.textBaseline = 'top';
            ctx2.fillText(label, centerX, centerY + 10);
        }, 1600);
    }

    initBarChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const chartData = data || {
            labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
            immature: [12, 15, 10, 18, 14, 9, 11],
            growing: [25, 22, 28, 24, 30, 26, 23],
            mature: [45, 48, 52, 46, 50, 55, 49],
            overripe: [8, 5, 10, 7, 6, 10, 8]
        };

        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: '幼嫩期',
                    data: chartData.immature,
                    backgroundColor: this.colors.immature,
                    borderRadius: 4
                }, {
                    label: '生长期',
                    data: chartData.growing,
                    backgroundColor: this.colors.growing,
                    borderRadius: 4
                }, {
                    label: '成熟期',
                    data: chartData.mature,
                    backgroundColor: this.colors.mature,
                    borderRadius: 4
                }, {
                    label: '过熟期',
                    data: chartData.overripe,
                    backgroundColor: this.colors.overripe,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { padding: 15, usePointStyle: true }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        padding: 12
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                        grid: { display: false }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        grid: { color: 'rgba(0,0,0,0.05)' }
                    }
                }
            }
        });
    }

    createMockData() {
        return {
            pieData: {
                labels: ['幼嫩期', '生长期', '成熟期', '过熟期'],
                values: [15, 25, 45, 15]
            },
            trendData: {
                labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
                mature: [150, 180, 165, 200, 190, 220, 210],
                growing: [80, 75, 90, 85, 95, 88, 92]
            },
            barData: {
                labels: ['茶叶', '烟叶', '桑叶', '生菜'],
                values: [85, 78, 92, 88]
            },
            radarData: {
                labels: ['绿色占比', '纹理特征', '形态指标', '光谱特征', '综合评分'],
                values: [82, 75, 88, 78, 85]
            }
        };
    }

    exportChart(canvasId, format = 'png') {
        const chart = this.charts[canvasId];
        if (!chart) return null;

        const link = document.createElement('a');
        link.download = `chart_${canvasId}_${new Date().toISOString().split('T')[0]}.${format}`;
        link.href = chart.toBase64Image();
        link.click();
    }

    destroyAll() {
        Object.keys(this.charts).forEach(key => {
            if (this.charts[key]) {
                this.charts[key].destroy();
            }
        });
        this.charts = {};
    }
}