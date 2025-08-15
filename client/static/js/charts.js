// healthcare_api_frontend/static/js/charts.js
/**
 * Healthcare Dashboard Charts Module
 * Manages all Chart.js visualizations
 */

class HealthcareChartsManager {
    constructor() {
        this.charts = {};
        this.updateInterval = null;
        console.log('HealthcareChartsManager initialized');
    }

    /**
     * Initialize all charts
     */
    async initializeCharts() {
        console.log('Initializing healthcare charts...');
        
        try {
            await this.createResponseTimeChart();
            await this.createMessageVolumeChart();
            await this.createHealthStatusChart();
            await this.createFHIRTrendsChart();
            
            console.log('All healthcare charts initialized successfully');
            
            // Start auto-update
            this.startAutoUpdate();
            
        } catch (error) {
            console.error('Error initializing charts:', error);
        }
    }

    /**
     * Create API Response Times Chart
     */
    async createResponseTimeChart() {
        const canvas = document.getElementById('responseTimeChart');
        if (!canvas) {
            console.warn('Response time chart canvas not found');
            return;
        }

        console.log('Creating response time chart...');

        try {
            const data = await window.apiClient.getResponseTimeAnalytics();
            
            this.charts.responseTime = new Chart(canvas.getContext('2d'), {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: data.datasets.map(dataset => ({
                        ...dataset,
                        backgroundColor: dataset.borderColor + '20',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: dataset.borderColor,
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 4
                    }))
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                            labels: {
                                usePointStyle: true,
                                padding: 20
                            }
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#ffffff',
                            bodyColor: '#ffffff',
                            borderColor: '#059669',
                            borderWidth: 1
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Response Time (ms)',
                                color: '#64748b'
                            },
                            grid: {
                                color: '#e2e8f0'
                            },
                            ticks: {
                                color: '#64748b'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Time of Day',
                                color: '#64748b'
                            },
                            grid: {
                                color: '#e2e8f0'
                            },
                            ticks: {
                                color: '#64748b'
                            }
                        }
                    },
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    }
                }
            });

            console.log('Response time chart created successfully');
            
        } catch (error) {
            console.error('Error creating response time chart:', error);
        }
    }

    /**
     * Create HL7 Message Volume Chart
     */
    async createMessageVolumeChart() {
        const canvas = document.getElementById('messageVolumeChart');
        if (!canvas) {
            console.warn('Message volume chart canvas not found');
            return;
        }

        console.log('Creating message volume chart...');

        try {
            const data = await window.apiClient.getMessageVolumeAnalytics();
            
            this.charts.messageVolume = new Chart(canvas.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: data.backgroundColor,
                        borderWidth: 4,
                        borderColor: '#ffffff',
                        hoverBorderWidth: 6,
                        hoverBorderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true,
                                font: {
                                    size: 12
                                }
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#ffffff',
                            bodyColor: '#ffffff',
                            borderColor: '#059669',
                            borderWidth: 1,
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${label}: ${value}% (${percentage}% of total)`;
                                }
                            }
                        }
                    },
                    cutout: '50%'
                }
            });

            console.log('Message volume chart created successfully');
            
        } catch (error) {
            console.error('Error creating message volume chart:', error);
        }
    }

    /**
     * Create Healthcare System Health Status Chart
     */
    async createHealthStatusChart() {
        const canvas = document.getElementById('healthStatusChart');
        if (!canvas) {
            console.warn('Health status chart canvas not found');
            return;
        }

        console.log('Creating health status chart...');

        try {
            const data = await window.apiClient.getSystemHealthAnalytics();
            
            this.charts.healthStatus = new Chart(canvas.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Uptime %',
                        data: data.data,
                        backgroundColor: data.backgroundColor,
                        borderRadius: 8,
                        borderSkipped: false,
                        borderWidth: 1,
                        borderColor: '#ffffff'
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
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#ffffff',
                            bodyColor: '#ffffff',
                            borderColor: '#059669',
                            borderWidth: 1,
                            callbacks: {
                                label: function(context) {
                                    return `Uptime: ${context.parsed.y.toFixed(1)}%`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'Uptime Percentage',
                                color: '#64748b'
                            },
                            grid: {
                                color: '#e2e8f0'
                            },
                            ticks: {
                                color: '#64748b',
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Healthcare Systems',
                                color: '#64748b'
                            },
                            grid: {
                                display: false
                            },
                            ticks: {
                                color: '#64748b',
                                maxRotation: 45
                            }
                        }
                    }
                }
            });

            console.log('Health status chart created successfully');
            
        } catch (error) {
            console.error('Error creating health status chart:', error);
        }
    }

    /**
     * Create FHIR Resource Processing Trends Chart
     */
    async createFHIRTrendsChart() {
        const canvas = document.getElementById('fhirTrendsChart');
        if (!canvas) {
            console.warn('FHIR trends chart canvas not found');
            return;
        }

        console.log('Creating FHIR trends chart...');

        try {
            // Generate FHIR resource data
            const fhirData = {
                labels: ['Patient', 'Observation', 'Encounter', 'Medication', 'DiagnosticReport'],
                data: [1247, 892, 634, 445, 321],
                backgroundColor: ['#0078d4', '#059669', '#e67e22', '#6b46c1', '#f59e0b']
            };
            
            this.charts.fhirTrends = new Chart(canvas.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: fhirData.labels,
                    datasets: [{
                        label: 'Resources Processed',
                        data: fhirData.data,
                        backgroundColor: fhirData.backgroundColor,
                        borderRadius: 6,
                        borderSkipped: false,
                        borderWidth: 1,
                        borderColor: '#ffffff'
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
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#ffffff',
                            bodyColor: '#ffffff',
                            borderColor: '#059669',
                            borderWidth: 1,
                            callbacks: {
                                label: function(context) {
                                    return `Resources: ${context.parsed.y.toLocaleString()}`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Number of Resources',
                                color: '#64748b'
                            },
                            grid: {
                                color: '#e2e8f0'
                            },
                            ticks: {
                                color: '#64748b',
                                callback: function(value) {
                                    return value.toLocaleString();
                                }
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'FHIR Resource Types',
                                color: '#64748b'
                            },
                            grid: {
                                display: false
                            },
                            ticks: {
                                color: '#64748b',
                                maxRotation: 45
                            }
                        }
                    }
                }
            });

            console.log('FHIR trends chart created successfully');
            
        } catch (error) {
            console.error('Error creating FHIR trends chart:', error);
        }
    }

    /**
     * Update all charts with new data
     */
    async updateAllCharts() {
        console.log('Updating all charts with new data...');

        try {
            // Update response time chart
            if (this.charts.responseTime) {
                const responseData = await window.apiClient.getResponseTimeAnalytics();
                this.charts.responseTime.data.datasets.forEach((dataset, index) => {
                    if (responseData.datasets[index]) {
                        dataset.data = responseData.datasets[index].data;
                    }
                });
                this.charts.responseTime.update('none');
            }

            // Update message volume chart
            if (this.charts.messageVolume) {
                const volumeData = await window.apiClient.getMessageVolumeAnalytics();
                this.charts.messageVolume.data.datasets[0].data = volumeData.data;
                this.charts.messageVolume.update('none');
            }

            // Update health status chart
            if (this.charts.healthStatus) {
                const healthData = await window.apiClient.getSystemHealthAnalytics();
                this.charts.healthStatus.data.datasets[0].data = healthData.data;
                this.charts.healthStatus.update('none');
            }

            // Update FHIR trends chart (simulate data variation)
            if (this.charts.fhirTrends) {
                const baseData = [1247, 892, 634, 445, 321];
                const newData = baseData.map(value => {
                    const variation = Math.floor(Math.random() * 100 - 50); // ±50 variation
                    return Math.max(100, value + variation);
                });
                this.charts.fhirTrends.data.datasets[0].data = newData;
                this.charts.fhirTrends.update('none');
            }

            console.log('All charts updated successfully');

        } catch (error) {
            console.error('Error updating charts:', error);
        }
    }

    /**
     * Start automatic chart updates
     */
    startAutoUpdate() {
        if (this.updateInterval) {
            console.log('Chart auto-update already running');
            return;
        }

        console.log('Starting automatic chart updates');
        this.updateInterval = setInterval(() => {
            this.updateAllCharts();
        }, 60000); // Update every minute
    }

    /**
     * Stop automatic chart updates
     */
    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
            console.log('Stopped automatic chart updates');
        }
    }

    /**
     * Resize all charts
     */
    resizeCharts() {
        console.log('Resizing all charts...');
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.resize === 'function') {
                chart.resize();
            }
        });
    }

    /**
     * Destroy all charts
     */
    destroyCharts() {
        console.log('Destroying all charts...');
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
        this.stopAutoUpdate();
    }
}

// Global charts manager
window.chartsManager = new HealthcareChartsManager();

// Initialize charts when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Charts module initializing...');
    
    // Wait for Chart.js to be fully loaded and API client to be ready
    setTimeout(async () => {
        try {
            await window.chartsManager.initializeCharts();
            console.log('Charts module initialized successfully');
        } catch (error) {
            console.error('Failed to initialize charts module:', error);
        }
    }, 1000); // Give API client time to initialize
});

// Handle window resize
window.addEventListener('resize', () => {
    if (window.chartsManager) {
        window.chartsManager.resizeCharts();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.chartsManager) {
        window.chartsManager.destroyCharts();
    }
    console.log('Charts module cleanup completed');
});