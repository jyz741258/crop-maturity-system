class PageManager {
    constructor() {
        this.currentPage = 'dashboard';
        this.sidebarCollapsed = false;
        this.isLoading = false;
        this.charts = {};
    }

    init() {
        console.log('PageManager.init() called');
        var self = this;
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                console.log('DOM fully loaded, calling initDashboard');
                self.bindAllEvents();
                self.initMockData();
                self.initDashboard();
                setTimeout(() => {
                    self.initCharts();
                }, 500);
            });
        } else {
            console.log('DOM already loaded, calling initDashboard immediately');
            this.bindAllEvents();
            this.initMockData();
            this.initDashboard();
            setTimeout(() => {
                this.initCharts();
            }, 500);
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
                
                var cropType = chip.dataset.crop;
                sessionStorage.setItem('selectedCrop', cropType);
                
                self.loadPage('analysis');
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
            // 检查本地存储的主题设置
            var savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'dark') {
                document.body.classList.add('dark-mode');
                var icon = themeToggle.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-moon');
                    icon.classList.add('fa-sun');
                }
            }
            
            themeToggle.addEventListener('click', function() {
                document.body.classList.toggle('dark-mode');
                var icon = themeToggle.querySelector('i');
                if (icon) {
                    icon.classList.toggle('fa-moon');
                    icon.classList.toggle('fa-sun');
                }
                
                // 保存主题设置到本地存储
                if (document.body.classList.contains('dark-mode')) {
                    localStorage.setItem('theme', 'dark');
                } else {
                    localStorage.setItem('theme', 'light');
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

        document.querySelectorAll('.dropdown-menu a').forEach(function(link) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                if (dropdown) dropdown.classList.remove('show');
                
                var href = link.getAttribute('href');
                
                if (href === '/logout') {
                    self.handleLogout();
                } else if (href === '#profile') {
                    self.showProfile();
                } else if (href === '#settings') {
                    self.showSettings();
                } else if (href === '#help-center') {
                    self.loadPage('help');
                }
            });
        });

        var notificationBtn = document.getElementById('notificationBtn');
        if (notificationBtn) {
            notificationBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                self.showNotifications();
            });
        }

        var searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('keydown', function(e) {
                if (e.keyCode === 13) {
                    e.preventDefault();
                    self.handleSearch(searchInput.value.trim());
                }
            });
        }

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

    handleLogout() {
        if (confirm('确定要退出登录吗？')) {
            fetch('/logout', {
                method: 'POST',
                credentials: 'include'
            })
            .then(function(response) {
                if (response.ok) {
                    window.location.href = '/login';
                }
            })
            .catch(function(error) {
                console.error('Logout error:', error);
                window.location.href = '/login';
            });
        }
    }

    showProfile() {
        var profileModal = document.createElement('div');
        profileModal.className = 'modal-overlay';
        profileModal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3><i class="fas fa-user"></i> 个人资料</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()"><i class="fas fa-times"></i></button>
                </div>
                <div class="modal-body">
                    <div class="profile-info">
                        <div class="profile-avatar">
                            <i class="fas fa-user"></i>
                        </div>
                        <div class="profile-details">
                            <div class="detail-item">
                                <label>用户名</label>
                                <span>admin</span>
                            </div>
                            <div class="detail-item">
                                <label>角色</label>
                                <span>系统管理员</span>
                            </div>
                            <div class="detail-item">
                                <label>邮箱</label>
                                <span>admin@crop-system.com</span>
                            </div>
                            <div class="detail-item">
                                <label>创建时间</label>
                                <span>2024-01-01</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">关闭</button>
                    <button class="btn btn-primary">修改资料</button>
                </div>
            </div>
        `;
        document.body.appendChild(profileModal);
        profileModal.addEventListener('click', function(e) {
            if (e.target === profileModal) {
                profileModal.remove();
            }
        });
    }

    showSettings() {
        var settingsModal = document.createElement('div');
        settingsModal.className = 'modal-overlay';
        settingsModal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3><i class="fas fa-cog"></i> 系统设置</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()"><i class="fas fa-times"></i></button>
                </div>
                <div class="modal-body">
                    <div class="settings-form">
                        <div class="setting-section">
                            <h4>界面设置</h4>
                            <div class="setting-item">
                                <label class="checkbox-label">
                                    <input type="checkbox" checked>
                                    <span>启用深色模式</span>
                                </label>
                            </div>
                            <div class="setting-item">
                                <label class="checkbox-label">
                                    <input type="checkbox" checked>
                                    <span>显示动画效果</span>
                                </label>
                            </div>
                        </div>
                        <div class="setting-section">
                            <h4>分析设置</h4>
                            <div class="setting-item">
                                <label>默认检测精度</label>
                                <select>
                                    <option>高</option>
                                    <option>中</option>
                                    <option>低</option>
                                </select>
                            </div>
                            <div class="setting-item">
                                <label class="checkbox-label">
                                    <input type="checkbox" checked>
                                    <span>自动保存分析结果</span>
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">取消</button>
                    <button class="btn btn-primary">保存设置</button>
                </div>
            </div>
        `;
        document.body.appendChild(settingsModal);
        settingsModal.addEventListener('click', function(e) {
            if (e.target === settingsModal) {
                settingsModal.remove();
            }
        });
    }

    showNotifications() {
        var notificationModal = document.createElement('div');
        notificationModal.className = 'modal-overlay';
        notificationModal.id = 'notificationModal';
        notificationModal.innerHTML = `
            <div class="modal-content" style="max-width: 450px;">
                <div class="modal-header">
                    <h3><i class="fas fa-bell"></i> 通知消息</h3>
                    <button class="modal-close" id="closeNotificationBtn"><i class="fas fa-times"></i></button>
                </div>
                <div class="modal-body" style="padding: 0;">
                    <div class="notification-list">
                        <div class="notification-item unread">
                            <div class="notification-icon success">
                                <i class="fas fa-check-circle"></i>
                            </div>
                            <div class="notification-content">
                                <div class="notification-title">分析任务完成</div>
                                <div class="notification-desc">您的甜椒种植区图片分析已完成，成熟率 85%</div>
                                <div class="notification-time">10分钟前</div>
                            </div>
                        </div>
                        <div class="notification-item unread">
                            <div class="notification-icon warning">
                                <i class="fas fa-exclamation-triangle"></i>
                            </div>
                            <div class="notification-content">
                                <div class="notification-title">作物成熟预警</div>
                                <div class="notification-desc">番茄大棚检测显示部分作物已达最佳采收期</div>
                                <div class="notification-time">30分钟前</div>
                            </div>
                        </div>
                        <div class="notification-item">
                            <div class="notification-icon info">
                                <i class="fas fa-info-circle"></i>
                            </div>
                            <div class="notification-content">
                                <div class="notification-title">系统更新</div>
                                <div class="notification-desc">系统已更新至 v2.1.0，新增批量分析功能</div>
                                <div class="notification-time">1小时前</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" id="markAllReadBtn">全部已读</button>
                    <button class="btn btn-primary" id="closeNotificationModalBtn">关闭</button>
                </div>
            </div>
        `;
        document.body.appendChild(notificationModal);
        
        var self = this;
        
        document.getElementById('closeNotificationBtn').addEventListener('click', function() {
            self.closeNotificationModal();
        });
        
        document.getElementById('markAllReadBtn').addEventListener('click', function() {
            self.closeNotificationModal();
        });
        
        document.getElementById('closeNotificationModalBtn').addEventListener('click', function() {
            self.closeNotificationModal();
        });
        
        notificationModal.addEventListener('click', function(e) {
            if (e.target === notificationModal) {
                self.closeNotificationModal();
            }
        });
    }
    
    closeNotificationModal() {
        var modal = document.getElementById('notificationModal');
        if (modal) {
            modal.remove();
        }
    }

    handleSearch(query) {
        if (!query) {
            this.showToast('请输入搜索关键词', 'info');
            return;
        }
        
        this.loadPage('history');
        
        setTimeout(function() {
            var searchInput = document.querySelector('.search-box-container input');
            if (searchInput) {
                searchInput.value = query;
                searchInput.dispatchEvent(new Event('input'));
            }
        }, 500);
        
        this.showToast('正在搜索: ' + query, 'info');
    }

    loadPage(pageName) {
        var self = this;
        console.log('loadPage called:', pageName);
        
        if (this.isLoading) {
            console.log('Already loading, ignoring');
            return;
        }
        if (pageName === this.currentPage) {
            console.log('Same page, ignoring');
            return;
        }

        this.isLoading = true;
        this.showLoading();
        console.log('Loading overlay shown');

        fetch('/' + pageName, {
            method: 'GET',
            credentials: 'include'
        })
            .then(function(response) {
                console.log('Response received:', response.status);
                if (!response.ok) {
                    throw new Error('HTTP error ' + response.status);
                }
                return response.text();
            })
            .then(function(content) {
                console.log('Content received, length:', content.length);
                var parser = new DOMParser();
                var doc = parser.parseFromString(content, 'text/html');
                var newMainContent = doc.querySelector('#mainContent');

                var mainContent = document.getElementById('mainContent');
                if (newMainContent && mainContent) {
                    console.log('Updating main content');
                    mainContent.innerHTML = newMainContent.innerHTML;
                    self.currentPage = pageName;
                    self.updateNavActive(pageName);
                    self.bindAllEvents();
                    self.initPageContent(pageName);
                } else {
                    console.error('Could not find #mainContent in response');
                }

                self.isLoading = false;
                self.hideLoading();
                console.log('Loading complete');
            })
            .catch(function(error) {
                console.error('Failed to load page:', error);
                self.isLoading = false;
                self.hideLoading();
                self.showToast('页面加载失败: ' + error.message, 'error');
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
                    var reportContent = self.generateHistoryReport();
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
        
        document.querySelectorAll('.pagination-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                if (btn.disabled) return;
                
                var pageNum = btn.textContent;
                var totalPages = 16;
                
                if (btn.querySelector('i')) {
                    var currentPage = document.querySelector('.pagination-btn.active');
                    if (currentPage) {
                        var currentNum = parseInt(currentPage.textContent);
                        if (btn.querySelector('.fa-chevron-left')) {
                            pageNum = Math.max(1, currentNum - 1).toString();
                        } else {
                            pageNum = Math.min(totalPages, currentNum + 1).toString();
                        }
                    }
                }
                
                var pageNumInt = parseInt(pageNum);
                if (isNaN(pageNumInt)) return;
                
                document.querySelectorAll('.pagination-btn').forEach(function(b) {
                    b.classList.remove('active');
                    b.disabled = false;
                });
                
                var firstBtn = document.querySelector('.pagination-btn:first-child');
                var lastBtn = document.querySelector('.pagination-btn:last-child');
                
                if (pageNumInt <= 1) {
                    if (firstBtn) firstBtn.disabled = true;
                }
                if (pageNumInt >= totalPages) {
                    if (lastBtn) lastBtn.disabled = true;
                }
                
                var targetBtn = Array.from(document.querySelectorAll('.pagination-btn')).find(function(b) {
                    return b.textContent === pageNum;
                });
                
                if (targetBtn) {
                    targetBtn.classList.add('active');
                    self.showToast('已切换到第 ' + pageNum + ' 页', 'info');
                }
            });
        });
    }

    generateHistoryReport() {
        var report = [];
        report.push('检测ID,文件名,作物类型,检测时间,成熟率,状态');
        
        var rows = document.querySelectorAll('#historyTableBody tr');
        rows.forEach(function(row) {
            var cells = row.querySelectorAll('td');
            if (cells.length >= 6) {
                var id = cells[0].textContent.trim();
                var filename = cells[1].textContent.trim();
                var crop = cells[2].textContent.trim();
                var time = cells[3].textContent.trim();
                var rate = cells[4].textContent.trim();
                var status = cells[5].textContent.trim();
                report.push([id, filename, crop, time, rate, status].join(','));
            }
        });
        
        report.push('');
        report.push('生成时间,' + new Date().toLocaleString('zh-CN'));
        report.push('记录总数,' + rows.length + ',条');
        
        return report.join('\n');
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
        console.log('initCharts called');
        console.log('window.Chart:', window.Chart);
        
        if (!window.Chart) {
            console.error('Chart.js is not loaded');
            return;
        }
        
        var self = this;
        
        setTimeout(function() {
            console.log('Initializing charts...');
            
            var maturityPie = document.getElementById('maturityPie');
            if (maturityPie) {
                console.log('Initializing maturityPie chart');
                try {
                    if (self.charts.maturityPie) {
                        self.charts.maturityPie.destroy();
                    }
                    self.charts.maturityPie = new Chart(maturityPie, {
                        type: 'doughnut',
                        data: {
                            labels: ['幼嫩期', '生长期', '成熟期', '过熟期'],
                            datasets: [{
                                data: [15, 25, 45, 15],
                                backgroundColor: ['#8bc34a', '#ffc107', '#4caf50', '#e53935'],
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
                                        usePointStyle: true
                                    }
                                }
                            }
                        }
                    });
                    console.log('maturityPie chart initialized');
                } catch (e) {
                    console.error('Error initializing maturityPie:', e);
                }
            }
            
            var trendChart = document.getElementById('trendChart');
            if (trendChart) {
                console.log('Initializing trendChart');
                try {
                    if (self.charts.trendChart) {
                        self.charts.trendChart.destroy();
                    }
                    self.charts.trendChart = new Chart(trendChart, {
                        type: 'line',
                        data: {
                            labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
                            datasets: [{
                                label: '成熟作物',
                                data: [150, 180, 165, 200, 190, 220, 210],
                                borderColor: '#4caf50',
                                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                                fill: true,
                                tension: 0.4,
                                pointRadius: 5,
                                pointHoverRadius: 8
                            }, {
                                label: '生长期作物',
                                data: [80, 75, 90, 85, 95, 88, 92],
                                borderColor: '#ffc107',
                                backgroundColor: 'rgba(255, 193, 7, 0.1)',
                                fill: true,
                                tension: 0.4,
                                pointRadius: 5,
                                pointHoverRadius: 8
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: { position: 'top' }
                            },
                            scales: {
                                y: { beginAtZero: true },
                                x: { grid: { display: false } }
                            }
                        }
                    });
                    console.log('trendChart initialized');
                } catch (e) {
                    console.error('Error initializing trendChart:', e);
                }
            }
            
            var qualityBar = document.getElementById('qualityBar');
            if (qualityBar) {
                console.log('Initializing qualityBar');
                try {
                    if (self.charts.qualityBar) {
                        self.charts.qualityBar.destroy();
                    }
                    self.charts.qualityBar = new Chart(qualityBar, {
                        type: 'bar',
                        data: {
                            labels: ['甜椒', '土豆', '番茄', '荔枝'],
                            datasets: [{
                                label: '品质评分',
                                data: [85, 78, 92, 88],
                                backgroundColor: ['#4caf50', '#ffc107', '#4caf50', '#4caf50'],
                                borderRadius: 8
                            }]
                        },
                        options: {
                            responsive: true,
                            indexAxis: 'y',
                            plugins: { legend: { display: false } },
                            scales: {
                                x: { min: 0, max: 100 }
                            }
                        }
                    });
                    console.log('qualityBar chart initialized');
                } catch (e) {
                    console.error('Error initializing qualityBar:', e);
                }
            }
            
            var radarChart = document.getElementById('radarChart');
            if (radarChart) {
                console.log('Initializing radarChart');
                try {
                    if (self.charts.radarChart) {
                        self.charts.radarChart.destroy();
                    }
                    self.charts.radarChart = new Chart(radarChart, {
                        type: 'radar',
                        data: {
                            labels: ['绿色占比', '纹理特征', '形态指标', '光谱特征', '综合评分'],
                            datasets: [{
                                label: '检测结果',
                                data: [82, 75, 88, 78, 85],
                                backgroundColor: 'rgba(46, 125, 50, 0.2)',
                                borderColor: '#2e7d32',
                                borderWidth: 2
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: { legend: { display: false } },
                            scales: {
                                r: { beginAtZero: true, max: 100 }
                            }
                        }
                    });
                    console.log('radarChart initialized');
                } catch (e) {
                    console.error('Error initializing radarChart:', e);
                }
            }
            
            var resultRadar = document.getElementById('resultRadar');
            if (resultRadar) {
                console.log('Initializing resultRadar');
                try {
                    if (self.charts.resultRadar) {
                        self.charts.resultRadar.destroy();
                    }
                    self.charts.resultRadar = new Chart(resultRadar, {
                        type: 'radar',
                        data: {
                            labels: ['绿色占比', '纹理特征', '形态指标', '光谱特征', '综合评分'],
                            datasets: [{
                                label: '检测结果',
                                data: [82, 75, 88, 78, 85],
                                backgroundColor: 'rgba(46, 125, 50, 0.2)',
                                borderColor: '#2e7d32',
                                borderWidth: 2
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: { legend: { display: false } },
                            scales: {
                                r: { beginAtZero: true, max: 100 }
                            }
                        }
                    });
                    console.log('resultRadar initialized');
                } catch (e) {
                    console.error('Error initializing resultRadar:', e);
                }
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
        var historyTableBody = document.getElementById('historyTableBody');
        if (!historyTableBody) return;

        var mockHistory = [
            { id: 'REC-2024-001', name: '甜椒种植区.jpg', crop: '甜椒', date: '2024-01-15 14:30:25', matureRate: 85 },
            { id: 'REC-2024-002', name: '土豆田航拍.jpg', crop: '土豆', date: '2024-01-14 10:15:42', matureRate: 78 },
            { id: 'REC-2024-003', name: '番茄大棚检测.jpg', crop: '番茄', date: '2024-01-13 16:45:18', matureRate: 92 },
            { id: 'REC-2024-004', name: '甜椒地块B.jpg', crop: '甜椒', date: '2024-01-12 09:20:33', matureRate: 88 },
            { id: 'REC-2024-005', name: '土豆样本集.jpg', crop: '土豆', date: '2024-01-11 11:30:55', matureRate: 72 }
        ];

        var self = this;
        historyTableBody.innerHTML = mockHistory.map(function(item, idx) {
            var rateClass = item.matureRate >= 80 ? 'high' : (item.matureRate >= 60 ? 'medium' : 'low');
            return '<tr style="animation: fade-in 0.3s ease-out ' + (idx * 0.05) + 's forwards; opacity: 0;">' +
                '<td>' + item.id + '</td>' +
                '<td class="file-name-cell">' + item.name + '</td>' +
                '<td>' + item.crop + '</td>' +
                '<td>' + item.date + '</td>' +
                '<td><span class="rate-badge ' + rateClass + '">' + item.matureRate + '%</span></td>' +
                '<td><span class="status-badge completed">已完成</span></td>' +
                '<td>' +
                '<button class="action-btn view-btn" onclick="pageManager.loadPage(\'result\')"><i class="fas fa-eye"></i></button>' +
                '<button class="action-btn download-btn" onclick="pageManager.downloadRecord(this)"><i class="fas fa-download"></i></button>' +
                '<button class="action-btn delete-btn" onclick="pageManager.deleteRecord(this)"><i class="fas fa-trash"></i></button>' +
                '</td>' +
                '</tr>';
        }).join('');
    }

    downloadRecord(btn) {
        var row = btn.closest('tr');
        var cells = row.querySelectorAll('td');
        var recordData = {
            id: cells[0].textContent,
            filename: cells[1].textContent,
            crop_type: cells[2].textContent,
            detect_time: cells[3].textContent,
            maturity_rate: cells[4].textContent
        };

        var csvContent = '记录ID,文件名,作物类型,检测时间,成熟率\n' +
            recordData.id + ',' +
            recordData.filename + ',' +
            recordData.crop_type + ',' +
            recordData.detect_time + ',' +
            recordData.maturity_rate;

        var blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        var link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = recordData.id + '.csv';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        this.showToast('记录已下载', 'success');
    }

    deleteRecord(btn) {
        if (confirm('确定要删除这条记录吗？')) {
            var row = btn.closest('tr');
            row.style.animation = 'fade-out 0.3s ease-out forwards';
            setTimeout(function() {
                row.remove();
            }, 300);
            this.showToast('记录已删除', 'success');
        }
    }

    setupSearchFilter() {
        var searchInput = document.querySelector('.search-box-container input');
        if (!searchInput) return;

        searchInput.addEventListener('input', function(e) {
            var query = e.target.value.toLowerCase();
            var tableRows = document.querySelectorAll('#historyTableBody tr');
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
            { id: 'Pepper__bell', name: '甜椒', icon: '🫑', desc: '果实成熟时呈绿色或红色，富含维生素C', standards: 'GB/T 19630-2005' },
            { id: 'Potato', name: '土豆', icon: '🥔', desc: '块茎作物，叶片繁茂期为最佳检测时机', standards: 'GB/T 8321-2012' },
            { id: 'Tomato', name: '番茄', icon: '🍅', desc: '果实成熟时颜色从绿转红，叶片健康直接影响产量', standards: 'GB/T 19175-2003' },
            { id: 'Lychee', name: '荔枝', icon: '🍒', desc: '常绿果树，叶片状态反映树体营养状况', standards: 'GB/T 18470-2001' }
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
        console.log('hideLoading called');
        var loadingOverlays = document.querySelectorAll('.loading-overlay');
        console.log('Found loading overlays:', loadingOverlays.length);
        
        loadingOverlays.forEach(function(overlay) {
            console.log('Removing loading overlay:', overlay);
            try {
                overlay.remove();
                console.log('Loading overlay removed successfully');
            } catch (e) {
                console.error('Error removing loading overlay:', e);
                overlay.style.display = 'none';
            }
        });
        
        var spinners = document.querySelectorAll('.spinner-container, .loading-spinner');
        spinners.forEach(function(spinner) {
            spinner.style.display = 'none';
        });
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