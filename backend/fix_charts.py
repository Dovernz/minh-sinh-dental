import re

with open('/app/templates/admin/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_logic = '''
            let barChart = new ApexCharts(document.querySelector("#barChart"), barOptions);
            barChart.render();

            // HEATMAP CHART
            const heatSeries = (chartData.heatmap && chartData.heatmap.length > 0) ? chartData.heatmap : [];
            const heatHeight = Math.max(480, heatSeries.length * 35);
            
            const heatmapOptions = {
                chart: { type: 'heatmap', height: heatHeight, toolbar: { show: false }, foreColor: textColor, background: 'transparent' },
                series: heatSeries,
                xaxis: { 
                    type: 'category', 
                    axisBorder: { show: false }, 
                    axisTicks: { show: false } 
                },
                plotOptions: {
                    heatmap: {
                        shadeIntensity: 0.5,
                        radius: 4,
                        useFillColorAsStroke: false,
                        colorScale: {
                            ranges: [
                                { from: 0, to: 0, color: isDark ? '#374151' : '#f3f4f6', name: 'Trống (0)' },
                                { from: 1, to: 2, color: '#93c5fd', name: 'Ít (1-2)' },
                                { from: 3, to: 5, color: '#3b82f6', name: 'Vừa (3-5)' },
                                { from: 6, to: 1000, color: '#1e40af', name: 'Đông (>5)' }
                            ]
                        }
                    }
                },
                dataLabels: { enabled: true },
                theme: { mode: isDark ? 'dark' : 'light' },
                tooltip: { theme: isDark ? 'dark' : 'light', y: { formatter: function (val) { return val + " khách" } } }
            };
            let heatmapChart = new ApexCharts(document.querySelector("#heatmapChart"), heatmapOptions);
            heatmapChart.render();

            document.addEventListener('themeChanged', function(e) {
                const isDark = e.detail.isDark;
                const newTextColor = isDark ? '#9ca3af' : '#6b7280';
                const newBorderColor = isDark ? '#374151' : '#f3f4f6';
                
                barChart.updateOptions({
                    chart: { foreColor: newTextColor },
                    theme: { mode: isDark ? 'dark' : 'light' },
                    tooltip: { theme: isDark ? 'dark' : 'light' },
                    grid: { borderColor: newBorderColor }
                });

                heatmapChart.updateOptions({
                    chart: { foreColor: newTextColor },
                    theme: { mode: isDark ? 'dark' : 'light' },
                    tooltip: { theme: isDark ? 'dark' : 'light' },
                    plotOptions: {
                        heatmap: {
                            colorScale: {
                                ranges: [
                                    { from: 0, to: 0, color: isDark ? '#374151' : '#f3f4f6', name: 'Trống (0)' },
                                    { from: 1, to: 2, color: '#93c5fd', name: 'Ít (1-2)' },
                                    { from: 3, to: 5, color: '#3b82f6', name: 'Vừa (3-5)' },
                                    { from: 6, to: 1000, color: '#1e40af', name: 'Đông (>5)' }
                                ]
                            }
                        }
                    }
                });
            });
'''

content = re.sub(r'new ApexCharts\(document\.querySelector\("#barChart"\), barOptions\)\.render\(\);.*?new ApexCharts\(document\.querySelector\("#heatmapChart"\), heatmapOptions\)\.render\(\);', new_logic, content, flags=re.DOTALL)

with open('/app/templates/admin/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
