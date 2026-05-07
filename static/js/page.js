class PageManager {
    constructor() {
        this.currentPage = 'dashboard';
        this.sidebarCollapsed = false;
        this.isLoading = false;
        this.charts = window.CropCharts ? new CropCharts() : null;
    }

    init() {
        console.log('PageManager.init() called');
        this.bindAllEvents();
        this.initMockData();
        this.initCharts();
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                console.log('DOM fully loaded, calling initDashboard');
                this.initDashboard();
            });
        } else {
            console.log('DOM already loaded, calling initDashboard immediately');
            this.initDashboard();
        }
    }

    bindAllEvents() {
        var self = this;
        
        document.querySelectorAll('.nav-link').forEach(function(link) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                var page = link.dataset.page;
                if (page) {
                    self.loadPage(page);
                }
            });
        });

        document.querySelectorAll('.action-btn[data-action]').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var action = btn.dataset.action;
                self.handleQuickAction(action);
            });
        });

        document.querySelectorAll('.crop-quick-select .crop-chip').forEach(function(chip) {
            chip.addEventListener('click', function() {
                document.querySelectorAll('.crop-quick-select .crop-chip').forEach(function(c) {
                    c.classList.remove('active');
                });
                chip.classList.add('active');
            });
        });

        var toggleBtn = document.getElementById('sidebarToggle');
        var sidebar = document.getElementById('sidebar');
        var mainContent = document.getElementById('mainContent');

        if (toggleBtn) {
            toggleBtn.addEventListener('click', function() {
                self.sidebarCollapsed = !self.sidebarCollapsed;
                if (sidebar) sidebar.classList.toggle('collapsed', self.sidebarCollapsed);
                if (mainContent) mainContent.classList.toggle('sidebar-collapsed', self.sidebarCollapsed);
            });
        }

        var themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', function() {
                document.body.classList.toggle('dark-mode');
                var icon = themeToggle.querySelector('i');
                if (icon) {
                    icon.classList.toggle('fa-moon');
                    icon.classList.toggle('fa-sun');
                }
            });
        }

        var menu = document.querySelector('.user-menu');
        var dropdown = document.getElementById('userDropdown');
        if (menu) {
            menu.addEventListener('click', function(e) {
                e.stopPropagation();
                if (dropdown) dropdown.classList.toggle('show');
            });
        }
        document.addEventListener('click', function(e) {
            if (menu && !menu.contains(e.target) && dropdown) {
                dropdown.classList.remove('show');
            }
        });

        document.querySelectorAll('.view-all').forEach(function(link) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                self.loadPage('history');
            });
        });

        document.querySelectorAll('.recent-item').forEach(function(item) {
            item.style.cursor = 'pointer';
            item.addEventListener('click', function() {
                self.loadPage('result');
            });
        });
    }

    handleQuickAction(action) {
        switch (action) {
            case 'new-analysis':
                this.loadPage('analysis');
                break;
            case 'upload-video':
                this.loadPage('batch');
                break;
            case 'generate-report':
                this.loadPage('history');
                break;
            case 'ai-assistant':
                window.open('/ai', '_blank');
                break;
            case 'region-analysis':
                window.open('/region', '_blank');
                break;
        }
    }

    loadPage(pageName) {
        var self = this;
        if (this.isLoading) return;
        if (pageName === this.currentPage) return;

        this.isLoading = true;
        this.showLoading();

        fetch('/' + pageName)
            .then(function(response) {
                if (!response.ok) throw new Error('页面加载失败');
                return response.text();
            })
            .then(function(content) {
                var parser = new DOMParser();
                var doc = parser.parseFromString(content, 'text/html');
                var newMainContent = doc.querySelector('#mainContent');

                var mainContent = document.getElementById('mainContent');
                if (newMainContent && mainContent) {
                    mainContent.innerHTML = newMainContent.innerHTML;
                    self.currentPage = pageName;
                    self.updateNavActive(pageName);
                    self.bindAllEvents();
                    self.initPageContent(pageName);
                }

                self.isLoading = false;
                self.hideLoading();
            })
            .catch(function(error) {
                console.error('Failed to load page:', error);
                self.isLoading = false;
                self.hideLoading();
                self.showToast('页面加载失败', 'error');
            });
    }

    updateNavActive(pageName) {
        document.querySelectorAll('.nav-link').forEach(function(link) {
            link.classList.remove('active');
            if (link.dataset.page === pageName) {
                link.classList.add('active');
            }
        });
    }

    initPageContent(pageName) {
        switch (pageName) {
            case 'dashboard':
                this.initDashboard();
                break;
            case 'analysis':
                this.initAnalysis();
                break;
            case 'batch':
                this.initBatch();
                break;
            case 'history':
                this.initHistory();
                break;
            case 'crops':
                this.initCrops();
                break;
            case 'help':
                this.initHelp();
                break;
            case 'result':
                this.initResult();
                break;
        }
    }

    initDashboard() {
        this.initCharts();
        this.initMockData();
        this.setupDashboardButtons();
    }

    setupDashboardButtons() {
        var self = this;
        
        console.log('setupDashboardButtons called');
        
        var refreshBtn = document.getElementById('refreshDataBtn');
        console.log('refreshBtn found:', !!refreshBtn);
        if (refreshBtn) {
            console.log('Adding click event to refreshBtn');
            refreshBtn.addEventListener('click', function() {
                console.log('Refresh button clicked');
                refreshBtn.disabled = true;
                refreshBtn.innerHTML = '<i class="fas fa-spinner" style="animation: spin 1s linear infinite;"></i> 刷新中...';
                
                setTimeout(function() {
                    self.initMockData();
                    self.initCharts();
                    refreshBtn.innerHTML = '<i class="fas fa-refresh"></i> 刷新数据';
                    refreshBtn.disabled = false;
                    self.showToast('数据已刷新', 'success');
                }, 1500);
            });
        }
        
        var exportBtn = document.getElementById('exportReportBtn');
        console.log('exportBtn found:', !!exportBtn);
        if (exportBtn) {
            console.log('Adding click event to exportBtn');
            exportBtn.addEventListener('click', function() {
                console.log('Export button clicked');
                exportBtn.disabled = true;
                exportBtn.innerHTML = '<i class="fas fa-spinner" style="animation: spin 1s linear infinite;"></i> 生成中...';
                
                setTimeout(function() {
                    var reportContent = generateDashboardReport();
                    var blob = new Blob([reportContent], { type: 'text/csv;charset=utf-8;' });
                    var link = document.createElement('a');
                    link.href = URL.createObjectURL(blob);
                    link.download = 'dashboard_report_' + new Date().toISOString().split('T')[0] + '.csv';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                    exportBtn.innerHTML = '<i class="fas fa-download"></i> 导出报告';
                    exportBtn.disabled = false;
                    self.showToast('报告已导出', 'success');
                }, 1000);
            });
        }
    }

    initAnalysis() {
        this.setupImageUpload();
        this.setupCropSelection();
        this.setupAnalyzeButton();
    }

    initBatch() {
        this.setupBatchUpload();
        this.setupBatchProcess();
    }

    initHistory() {
        this.loadHistoryData();
        this.setupSearchFilter();
        this.setupHistoryButtons();
    }

    setupHistoryButtons() {
        var self = this;
        
        var filterBtn = document.getElementById('filterBtn');
        if (filterBtn) {
            filterBtn.addEventListener('click', function() {
                var filterBar = document.querySelector('.filter-bar');
                if (filterBar) {
                    filterBar.classList.toggle('show');
                }
            });
        }
        
        var exportBtn = document.getElementById('exportHistoryBtn');
        if (exportBtn) {
            exportBtn.addEventListener('click', function() {
                exportBtn.disabled = true;
                exportBtn.innerHTML = '<i class="fas fa-spinner" style="animation: spin 1s linear infinite;"></i> 导出中...';
                
                setTimeout(function() {
                    var reportContent = generateHistoryReport();
                    var blob = new Blob([reportContent], { type: 'text/csv;charset=utf-8;' });
                    var link = document.createElement('a');
                    link.href = URL.createObjectURL(blob);
                    link.download = 'history_report_' + new Date().toISOString().split('T')[0] + '.csv';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                    exportBtn.innerHTML = '<i class="fas fa-download"></i> 导出';
                    exportBtn.disabled = false;
                    self.showToast('历史记录已导出', 'success');
                }, 1000);
            });
        }
        
        document.querySelectorAll('.view-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                self.loadPage('result');
            });
        });
        
        document.querySelectorAll('.download-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                self.showToast('下载功能开发中', 'info');
            });
        });
        
        document.querySelectorAll('.delete-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                if (confirm('确定要删除这条记录吗？')) {
                    btn.parentElement.parentElement.remove();
                    self.showToast('记录已删除', 'success');
                }
            });
        });
        
        document.querySelectorAll('.pagination-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                if (!btn.disabled) {
                    document.querySelectorAll('.pagination-btn').forEach(function(b) {
                        b.classList.remove('active');
                    });
                    btn.classList.add('active');
                    self.showToast('已切换到第 ' + btn.textContent + ' 页', 'info');
                }
            });
        });
    }

    initCrops() {
        this.loadCropList();
    }

    initHelp() {
        this.setupHelpNavigation();
    }

    initResult() {
        console.log('initResult called');
        this.initCharts();
        this.setupDownloadReport();
        this.setupDownloadReportDirect();
    }

    setupDownloadReportDirect() {
        var downloadBtn = document.getElementById('downloadReportBtn');
        if (!downloadBtn) {
            console.log('downloadBtn not found');
            return;
        }

        downloadBtn.addEventListener('click', function() {
            downloadBtn.disabled = true;
            downloadBtn.innerHTML = '<i class="fas fa-spinner" style="animation: spin 1s linear infinite;"></i> 生成中...';

            var reportData = {
                results: [],
                crop_type: 'tea'
            };

            var rows = document.querySelectorAll('#detailTableBody tr');
            if (rows.length > 0) {
                rows.forEach(function(row, idx) {
                    var cells = row.querySelectorAll('td');
                    reportData.results.push({
                        id: 'REC-' + String(idx + 1).padStart(3, '0'),
                        maturity: cells[2].textContent.trim(),
                        confidence: parseFloat(cells[3].textContent),
                        green_ratio: parseFloat(cells[4].textContent) / 100,
                        quality_score: parseFloat(cells[5].textContent),
                        bbox: [0, 0, 100, 100]
                    });
                });
            } else {
                reportData.results = [
                    { id: 'REC-001', maturity: '成熟期', confidence: 95.5, green_ratio: 0.85, quality_score: 92, bbox: [0, 0, 100, 100] },
                    { id: 'REC-002', maturity: '成熟期', confidence: 93.2, green_ratio: 0.82, quality_score: 88, bbox: [0, 0, 100, 100] },
                    { id: 'REC-003', maturity: '生长期', confidence: 88.7, green_ratio: 0.72, quality_score: 75, bbox: [0, 0, 100, 100] }
                ];
            }

            console.log('Report data to send:', reportData);

            fetch('/api/generate_report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(reportData),
                credentials: 'include'
            })
            .then(function(response) {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    return response.json().then(function(errData) {
                        throw new Error(errData.error || '生成报告失败，状态码: ' + response.status);
                    });
                }
                return response.json();
            })
            .then(function(data) {
                if (data.success && data.download_url) {
                    var link = document.createElement('a');
                    link.href = data.download_url;
                    link.download = 'analysis_report.csv';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    downloadBtn.innerHTML = '<i class="fas fa-check-circle"></i> 下载完成';
                    setTimeout(function() {
                        downloadBtn.innerHTML = '<i class="fas fa-download"></i> 下载报告';
                        downloadBtn.disabled = false;
                    }, 2000);
                } else {
                    throw new Error(data.error || '生成报告失败');
                }
            })
            .catch(function(error) {
                console.error('Download report error:', error);
                downloadBtn.innerHTML = '<i class="fas fa-download"></i> 下载报告';
                downloadBtn.disabled = false;
                alert('下载报告失败: ' + error.message);
            });
        });
    }

    setupDownloadReport() {
        console.log('setupDownloadReport called');
        var downloadBtn = document.getElementById('downloadReportBtn');
        console.log('downloadBtn:', downloadBtn);
        if (!downloadBtn) {
            console.log('downloadBtn not found');
            return;
        }

        downloadBtn.addEventListener('click', function() {
            downloadBtn.disabled = true;
            downloadBtn.innerHTML = '<i class="fas fa-spinner" style="animation: spin 1s linear infinite;"></i> 生成中...';

            var reportData = {
                results: [],
                crop_type: 'tea'
            };

            var rows = document.querySelectorAll('#detailTableBody tr');
            if (rows.length > 0) {
                rows.forEach(function(row, idx) {
                    var cells = row.querySelectorAll('td');
                    reportData.results.push({
                        id: 'REC-' + String(idx + 1).padStart(3, '0'),
                        maturity: cells[2].textContent.trim(),
                        confidence: parseFloat(cells[3].textContent),
                        green_ratio: parseFloat(cells[4].textContent) / 100,
                        quality_score: parseFloat(cells[5].textContent),
                        bbox: [0, 0, 100, 100]
                    });
                });
            } else {
                reportData.results = [
                    { id: 'REC-001', maturity: '成熟期', confidence: 95.5, green_ratio: 0.85, quality_score: 92, bbox: [0, 0, 100, 100] },
                    { id: 'REC-002', maturity: '成熟期', confidence: 93.2, green_ratio: 0.82, quality_score: 88, bbox: [0, 0, 100, 100] },
                    { id: 'REC-003', maturity: '生长期', confidence: 88.7, green_ratio: 0.72, quality_score: 75, bbox: [0, 0, 100, 100] }
                ];
            }

            console.log('Report data to send:', reportData);
            
            fetch('/api/generate_report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(reportData),
                credentials: 'include'
            })
            .then(function(response) {
                console.log('Response status:', response.status);
                console.log('Response headers:', response.headers);
                if (!response.ok) {
                    response.json().then(function(errData) {
                        console.error('Error response:', errData);
                    });
                    throw new Error('生成报告失败，状态码: ' + response.status);
                }
                return response.json();
            })
            .then(function(data) {
                if (data.success && data.download_url) {
                    var link = document.createElement('a');
                    link.href = data.download_url;
                    link.download = 'analysis_report.csv';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    downloadBtn.innerHTML = '<i class="fas fa-check-circle"></i> 下载完成';
                    setTimeout(function() {
                        downloadBtn.innerHTML = '<i class="fas fa-download"></i> 下载报告';
                        downloadBtn.disabled = false;
                    }, 2000);
                } else {
                    throw new Error(data.error || '生成报告失败');
                }
            })
            .catch(function(error) {
                console.error('Download report error:', error);
                downloadBtn.innerHTML = '<i class="fas fa-download"></i> 下载报告';
                downloadBtn.disabled = false;
                alert('下载报告失败: ' + error.message);
            });
        });
    }

    initCharts() {
        if (!this.charts) return;
        var self = this;

        setTimeout(function() {
            if (document.getElementById('maturityPie')) {
                self.charts.initMaturityPieChart('maturityPie', self.charts.createMockData().pieData);
            }
            if (document.getElementById('trendChart')) {
                self.charts.initTrendLineChart('trendChart', self.charts.createMockData().trendData);
            }
            if (document.getElementById('radarChart')) {
                self.charts.initRadarChart('radarChart', self.charts.createMockData().radarData);
            }
            if (document.getElementById('qualityBar')) {
                self.charts.initQualityBarChart('qualityBar', self.charts.createMockData().barData);
            }
            if (document.getElementById('resultRadar')) {
                self.charts.initRadarChart('resultRadar', {
                    labels: ['绿色占比', '纹理特征', '形态指标', '光谱特征', '综合评分'],
                    values: [82, 75, 88, 78, 85]
                });
            }
        }, 300);
    }

    initMockData() {
        this.loadRecentList();
        this.loadStatsSummary();
    }

    loadRecentList() {
        var recentList = document.getElementById('recentList');
        if (!recentList) return;

        var mockRecent = [
            { id: 1, name: '甜椒种植区.jpg', crop: '甜椒', date: '10分钟前', matureRate: 85 },
            { id: 2, name: '土豆田航拍.jpg', crop: '土豆', date: '30分钟前', matureRate: 78 },
            { id: 3, name: '番茄大棚检测.jpg', crop: '番茄', date: '1小时前', matureRate: 92 }
        ];

        var self = this;
        recentList.innerHTML = mockRecent.map(function(item) {
            return '<div class="recent-item" style="cursor:pointer;">' +
                '<div class="recent-thumb" style="background: linear-gradient(135deg, #2e7d32, #43a047);">' +
                '<i class="fas fa-image"></i>' +
                '</div>' +
                '<div class="recent-info">' +
                '<div class="recent-name">' + item.name + '</div>' +
                '<div class="recent-meta">' + item.crop + ' · ' + item.date + '</div>' +
                '</div>' +
                '<div class="recent-rate">' + item.matureRate + '%</div>' +
                '</div>';
        }).join('');

        recentList.querySelectorAll('.recent-item').forEach(function(item) {
            item.addEventListener('click', function() {
                self.loadPage('result');
            });
        });
    }

    loadStatsSummary() {
        var statValues = document.querySelectorAll('.stats-overview .stat-value');
        var values = [3221, 2456, 86.5, 2];

        for (var i = 0; i < statValues.length; i++) {
            this.animateNumber(statValues[i], 0, values[i], 1500);
        }
    }

    animateNumber(element, start, end, duration) {
        var startTime = performance.now();
        var animate = function(currentTime) {
            var elapsed = currentTime - startTime;
            var progress = Math.min(elapsed / duration, 1);
            var easeOut = 1 - Math.pow(1 - progress, 3);
            var current = Math.floor(start + (end - start) * easeOut);
            element.textContent = current;

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        requestAnimationFrame(animate);
    }

    setupImageUpload() {
        var uploadArea = document.getElementById('uploadArea');
        var fileInput = document.getElementById('fileInput');
        var previewSection = document.getElementById('previewSection');
        var self = this;

        if (!uploadArea || !fileInput) return;

        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', function() {
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            self.handleFileDrop(e.dataTransfer.files, previewSection);
        });

        fileInput.addEventListener('change', function(e) {
            self.handleFileDrop(e.target.files, previewSection);
        });

        uploadArea.addEventListener('click', function() {
            fileInput.click();
        });
    }

    handleFileDrop(files, previewSection) {
        var file = files[0];
        var self = this;

        if (file && file.type.startsWith('image/')) {
            var reader = new FileReader();
            reader.onload = function(e) {
                previewSection.innerHTML = '<img src="' + e.target.result + '" class="preview-image" alt="预览">' +
                    '<div class="preview-info">' +
                    '<span>' + file.name + '</span>' +
                    '<span>' + (file.size / 1024).toFixed(1) + ' KB</span>' +
                    '</div>';
            };
            reader.readAsDataURL(file);
            self.showToast('图片上传成功', 'success');
        }
    }

    setupCropSelection() {
        document.querySelectorAll('.crop-chip').forEach(function(chip) {
            chip.addEventListener('click', function() {
                document.querySelectorAll('.crop-chip').forEach(function(c) {
                    c.classList.remove('active');
                });
                chip.classList.add('active');
            });
        });
    }

    setupAnalyzeButton() {
        var analyzeBtn = document.getElementById('analyzeBtn');
        var self = this;

        if (!analyzeBtn) return;

        analyzeBtn.addEventListener('click', function() {
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<i class="fas fa-spinner" style="animation: spin 1s linear infinite;"></i> 分析中...';

            setTimeout(function() {
                self.loadPage('result');
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = '<i class="fas fa-play"></i> 开始分析';
            }, 2000);
        });
    }

    setupBatchUpload() {
        var dropZone = document.getElementById('batchDropZone');
        var batchFileInput = document.getElementById('batchFileInput');
        var self = this;

        if (!dropZone || !batchFileInput) return;

        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });

        dropZone.addEventListener('dragleave', function() {
            dropZone.classList.remove('drag-over');
        });

        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            self.handleBatchDrop(e.dataTransfer.files);
        });

        batchFileInput.addEventListener('change', function(e) {
            self.handleBatchDrop(e.target.files);
        });

        dropZone.addEventListener('click', function() {
            batchFileInput.click();
        });
    }

    handleBatchDrop(files) {
        var fileGrid = document.getElementById('fileGrid');
        var filesArray = Array.from(files).filter(function(f) {
            return f.type.startsWith('image/');
        });

        filesArray.forEach(function(file, idx) {
            var reader = new FileReader();
            reader.onload = function(e) {
                var fileCard = document.createElement('div');
                fileCard.className = 'file-card';
                fileCard.style.opacity = '0';
                fileCard.style.animation = 'fade-in 0.3s ease-out ' + (idx * 0.05) + 's forwards';
                fileCard.innerHTML = '<img src="' + e.target.result + '" alt="' + file.name + '">' +
                    '<div class="file-info">' +
                    '<span class="file-name">' + file.name + '</span>' +
                    '<span class="file-size">' + (file.size / 1024).toFixed(1) + ' KB</span>' +
                    '</div>' +
                    '<div class="file-actions">' +
                    '<button class="remove-btn"><i class="fas fa-times"></i></button>' +
                    '</div>';
                if (fileGrid) fileGrid.appendChild(fileCard);

                var removeBtn = fileCard.querySelector('.remove-btn');
                if (removeBtn) {
                    removeBtn.addEventListener('click', function() {
                        fileCard.remove();
                    });
                }
            };
            reader.readAsDataURL(file);
        });
    }

    setupBatchProcess() {
        var processBtn = document.getElementById('processBatchBtn');
        var progressBar = document.getElementById('batchProgress');

        if (!processBtn) return;

        processBtn.addEventListener('click', function() {
            progressBar.style.display = 'block';
            processBtn.disabled = true;

            var progress = 0;
            var progressBarElement = progressBar.querySelector('.progress-bar');
            var progressText = progressBar.querySelector('.progress-text');
            var self = this;

            var updateProgress = function() {
                if (progress <= 100) {
                    progressBarElement.style.width = progress + '%';
                    progressText.textContent = Math.floor(progress) + '%';
                    progress += Math.random() * 15;
                    setTimeout(updateProgress, 50);
                } else {
                    progressBarElement.style.width = '100%';
                    progressText.textContent = '完成';
                    setTimeout(function() {
                        progressBar.style.display = 'none';
                        processBtn.disabled = false;
                        self.showToast('批量分析完成！', 'success');
                    }, 500);
                }
            };
            updateProgress();
        }.bind(this));
    }

    loadHistoryData() {
        var historyTable = document.getElementById('historyTable');
        if (!historyTable) return;

        var mockHistory = [
            { id: 'REC-001', name: '大田地块A.jpg', crop: '生菜', date: '2024-01-15 14:30', matureRate: 75 },
            { id: 'REC-002', name: '茶园航拍.mp4', crop: '茶叶', date: '2024-01-14 10:15', matureRate: 82 },
            { id: 'REC-003', name: '菠菜种植区.jpg', crop: '菠菜', date: '2024-01-13 16:45', matureRate: 68 },
            { id: 'REC-004', name: '芹菜基地.jpg', crop: '芹菜', date: '2024-01-12 09:20', matureRate: 90 },
            { id: 'REC-005', name: '烟叶田块B.jpg', crop: '烟叶', date: '2024-01-11 11:30', matureRate: 73 }
        ];

        historyTable.innerHTML = mockHistory.map(function(item, idx) {
            var rateClass = item.matureRate >= 80 ? 'high' : (item.matureRate >= 60 ? 'medium' : 'low');
            return '<tr style="animation: fade-in 0.3s ease-out ' + (idx * 0.05) + 's forwards; opacity: 0;">' +
                '<td>' + item.id + '</td>' +
                '<td class="file-name-cell">' + item.name + '</td>' +
                '<td>' + item.crop + '</td>' +
                '<td>' + item.date + '</td>' +
                '<td><span class="rate-badge ' + rateClass + '">' + item.matureRate + '%</span></td>' +
                '<td>' +
                '<button class="action-btn view-btn" onclick="pageManager.loadPage(\'result\')"><i class="fas fa-eye"></i></button>' +
                '<button class="action-btn download-btn"><i class="fas fa-download"></i></button>' +
                '<button class="action-btn delete-btn"><i class="fas fa-trash"></i></button>' +
                '</td>' +
                '</tr>';
        }).join('');
    }

    setupSearchFilter() {
        var searchInput = document.querySelector('.search-box input');
        if (!searchInput) return;

        searchInput.addEventListener('input', function(e) {
            var query = e.target.value.toLowerCase();
            var tableRows = document.querySelectorAll('#historyTable tr');
            tableRows.forEach(function(row) {
                var text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    }

    loadCropList() {
        var cropGrid = document.getElementById('cropGrid');
        if (!cropGrid) return;

        var crops = [
            { id: 'tea', name: '茶叶', icon: '🍵', desc: '适制高档绿茶、名优茶', standards: 'GB/T 23776-2018' },
            { id: 'tobacco', name: '烟叶', icon: '🚬', desc: '最佳采收期，品质最优', standards: 'GB 2635-2018' },
            { id: 'mulberry', name: '桑叶', icon: '🐛', desc: '适用于大蚕饲养', standards: 'NY/T 1187-2006' },
            { id: 'lettuce', name: '生菜', icon: '🥬', desc: '商品价值最高', standards: 'GB/T 18407.1-2001' },
            { id: 'spinach', name: '菠菜', icon: '🌿', desc: '营养丰富', standards: 'NY/T 5008-2016' },
            { id: 'celery', name: '芹菜', icon: '🥕', desc: '叶柄粗壮，口感脆嫩', standards: 'NY/T 5008-2016' }
        ];

        cropGrid.innerHTML = crops.map(function(crop, idx) {
            return '<div class="crop-card" style="animation: fade-in 0.3s ease-out ' + (idx * 0.1) + 's forwards; opacity: 0;">' +
                '<div class="crop-icon">' + crop.icon + '</div>' +
                '<div class="crop-name">' + crop.name + '</div>' +
                '<div class="crop-desc">' + crop.desc + '</div>' +
                '<div class="crop-standards">' + crop.standards + '</div>' +
                '<button class="btn btn-primary btn-sm" onclick="pageManager.loadPage(\'analysis\')">选择</button>' +
                '</div>';
        }).join('');
    }

    setupHelpNavigation() {
        var helpItems = document.querySelectorAll('.help-item');

        helpItems.forEach(function(item) {
            item.addEventListener('click', function() {
                helpItems.forEach(function(i) {
                    i.classList.remove('active');
                });
                item.classList.add('active');

                var contentId = item.dataset.content;
                document.querySelectorAll('.help-content').forEach(function(c) {
                    c.style.display = 'none';
                });
                var content = document.getElementById(contentId);
                if (content) {
                    content.style.display = 'block';
                }
            });
        });
    }

    showLoading() {
        var loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.innerHTML = '<div class="spinner-container">' +
            '<div class="spinner" style="animation: spin 1s linear infinite;"></div>' +
            '<span>加载中...</span>' +
            '</div>';
        document.body.appendChild(loadingOverlay);
    }

    hideLoading() {
        var loadingOverlay = document.querySelector('.loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.remove();
        }
    }

    showToast(message, type) {
        if (type === undefined) type = 'success';
        
        var toast = document.createElement('div');
        toast.className = 'toast toast-' + type;
        toast.style.animation = 'fade-in 0.3s ease-out';
        
        var iconClass = 'check-circle';
        if (type === 'error') iconClass = 'exclamation-circle';
        else if (type === 'info') iconClass = 'info-circle';
        
        toast.innerHTML = '<i class="fas fa-' + iconClass + '"></i>' +
            '<span>' + message + '</span>' +
            '<button class="toast-close"><i class="fas fa-times"></i></button>';

        document.body.appendChild(toast);

        var closeBtn = toast.querySelector('.toast-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                toast.remove();
            });
        }

        setTimeout(function() {
            toast.remove();
        }, 4000);
    }
}

function generateDashboardReport() {
    var report = [];
    report.push('指标名称,数值,单位');
    
    var statTotal = document.getElementById('statTotal');
    if (statTotal) report.push('今日检测总数,' + statTotal.textContent + ',次');
    
    var statMature = document.getElementById('statMature');
    if (statMature) report.push('成熟作物数,' + statMature.textContent + ',株');
    
    var statYoung = document.getElementById('statYoung');
    if (statYoung) report.push('幼嫩作物数,' + statYoung.textContent + ',株');
    
    var statRate = document.getElementById('statRate');
    if (statRate) report.push('成熟率,' + statRate.textContent + ',');
    
    report.push('');
    report.push('生成时间,' + new Date().toLocaleString('zh-CN') + ',');
    
    return report.join('\n');
}

function generateHistoryReport() {
    var report = [];
    report.push('检测ID,检测时间,作物类型,成熟度,置信度,品质评分');
    
    var rows = document.querySelectorAll('.history-item');
    rows.forEach(function(row, idx) {
        var id = 'REC-' + String(idx + 1).padStart(4, '0');
        var time = row.querySelector('.history-time');
        var crop = row.querySelector('.history-crop');
        var maturity = row.querySelector('.history-maturity');
        var confidence = row.querySelector('.history-confidence');
        var quality = row.querySelector('.history-quality');
        
        var timeText = time ? time.textContent : '';
        var cropText = crop ? crop.textContent : '';
        var maturityText = maturity ? maturity.textContent : '';
        var confidenceText = confidence ? confidence.textContent : '';
        var qualityText = quality ? quality.textContent : '';
        
        report.push([id, timeText, cropText, maturityText, confidenceText, qualityText].join(','));
    });
    
    report.push('');
    report.push('生成时间,' + new Date().toLocaleString('zh-CN'));
    report.push('记录总数,' + rows.length + ',条');
    
    return report.join('\n');
}

document.addEventListener('DOMContentLoaded', function() {
    window.pageManager = new PageManager();
    window.pageManager.init();
});