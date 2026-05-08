import os

# 模板文件内容
templates = {
    'analysis.html': '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>作物成熟度分析系统 - 单图分析</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link rel="stylesheet" href="/static/css/style.css">
    <link rel="stylesheet" href="/static/css/responsive.css">
    <link rel="stylesheet" href="/static/css/animations.css">
</head>
<body>
    {% include 'navbar.html' %}
    
    <div class="app-container">
        {% include 'sidebar.html' %}
        
        <main class="main-content" id="mainContent">
            <div class="page-header animate-fade-in">
                <h1>单图分析</h1>
                <p>上传单张图片进行作物成熟度检测</p>
            </div>

            <div class="analysis-container">
                <div class="upload-section animate-fade-in" style="animation-delay: 0.1s">
                    <div class="section-header">
                        <h2><i class="fas fa-upload"></i> 上传图片</h2>
                    </div>
                    
                    <div class="upload-area" id="uploadArea">
                        <div class="upload-icon">
                            <i class="fas fa-cloud-upload-alt"></i>
                        </div>
                        <p>点击或拖拽上传图片</p>
                        <p class="upload-hint">支持 JPG、PNG、BMP 格式，最大50MB</p>
                        <input type="file" id="fileInput" accept="image/*" style="display: none">
                    </div>
                    
                    <div class="preview-section" id="previewSection">
                        <div class="preview-placeholder">
                            <i class="fas fa-image"></i>
                            <p>图片预览区域</p>
                        </div>
                    </div>
                </div>

                <div class="settings-section animate-fade-in" style="animation-delay: 0.2s">
                    <div class="section-header">
                        <h2><i class="fas fa-cog"></i> 检测设置</h2>
                    </div>
                    
                    <div class="settings-card">
                        <div class="setting-item">
                            <label>作物类型</label>
                            <div class="crop-selector" id="cropSelector">
                                <div class="crop-chip active" data-crop="Pepper__bell">
                                    <span>🫑</span>
                                    <span>甜椒</span>
                                </div>
                                <div class="crop-chip" data-crop="Potato">
                                    <span>🥔</span>
                                    <span>土豆</span>
                                </div>
                                <div class="crop-chip" data-crop="Tomato">
                                    <span>🍅</span>
                                    <span>番茄</span>
                                </div>
                                <div class="crop-chip" data-crop="Lychee">
                                    <span>🍒</span>
                                    <span>荔枝</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="setting-item">
                            <div class="setting-label">
                                <span>检测精度</span>
                                <span class="setting-value">高</span>
                            </div>
                            <input type="range" id="precisionSlider" min="1" max="100" value="85">
                            <div class="slider-labels">
                                <span>低</span>
                                <span>中</span>
                                <span>高</span>
                            </div>
                        </div>
                        
                        <div class="setting-item">
                            <label class="checkbox-label">
                                <input type="checkbox" id="enableEnhance">
                                <span>启用图像增强</span>
                            </label>
                        </div>
                    </div>
                </div>

                <div class="action-section animate-fade-in" style="animation-delay: 0.3s">
                    <button class="btn btn-primary btn-lg" id="analyzeBtn">
                        <i class="fas fa-play"></i> 开始分析
                    </button>
                    <button class="btn btn-secondary btn-lg" id="resetBtn">
                        <i class="fas fa-refresh"></i> 重置
                    </button>
                </div>
            </div>
        </main>
    </div>

    <script src="/static/js/page.js"></script>
</body>
</html>''',

    'batch.html': '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>作物成熟度分析系统 - 批量分析</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link rel="stylesheet" href="/static/css/style.css">
    <link rel="stylesheet" href="/static/css/responsive.css">
    <link rel="stylesheet" href="/static/css/animations.css">
</head>
<body>
    {% include 'navbar.html' %}
    
    <div class="app-container">
        {% include 'sidebar.html' %}
        
        <main class="main-content" id="mainContent">
            <div class="page-header animate-fade-in">
                <h1>批量分析</h1>
                <p>一次性处理多张图片进行批量检测</p>
                <div class="header-actions">
                    <button class="btn btn-primary" id="exportBatchBtn"><i class="fas fa-download"></i> 导出报告</button>
                </div>
            </div>

            <div class="batch-container">
                <div class="upload-zone animate-fade-in" style="animation-delay: 0.1s">
                    <div class="drop-zone" id="dropZone">
                        <div class="drop-icon">
                            <i class="fas fa-images"></i>
                        </div>
                        <p>拖拽图片到此处</p>
                        <p class="drop-hint">支持 JPG、PNG、BMP 格式，可多选</p>
                        <input type="file" id="batchFileInput" accept="image/*" multiple style="display: none">
                    </div>
                    
                    <div class="file-grid" id="fileGrid">
                        <div class="empty-hint">
                            <i class="fas fa-folder-open"></i>
                            <p>暂无上传的文件</p>
                        </div>
                    </div>
                </div>

                <div class="batch-settings animate-fade-in" style="animation-delay: 0.2s">
                    <div class="section-header">
                        <h2><i class="fas fa-cog"></i> 批量设置</h2>
                    </div>
                    
                    <div class="settings-row">
                        <div class="setting-item">
                            <label>作物类型</label>
                            <select class="setting-select" id="batchCropSelect">
                                <option value="Pepper__bell">甜椒</option>
                                <option value="Potato">土豆</option>
                                <option value="Tomato">番茄</option>
                                <option value="Lychee">荔枝</option>
                            </select>
                        </div>
                        
                        <div class="setting-item">
                            <label>处理模式</label>
                            <select class="setting-select" id="processMode">
                                <option value="parallel">并行处理</option>
                                <option value="sequential">顺序处理</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div class="batch-progress animate-fade-in" style="animation-delay: 0.3s" id="progressSection" style="display: none">
                    <div class="progress-header">
                        <span>处理进度</span>
                        <span class="progress-text" id="progressText">0/0</span>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar" id="progressBar"></div>
                    </div>
                    <div class="progress-info" id="progressInfo">准备开始...</div>
                </div>

                <div class="batch-actions animate-fade-in" style="animation-delay: 0.4s">
                    <button class="btn btn-primary btn-lg" id="batchAnalyzeBtn">
                        <i class="fas fa-play"></i> 批量分析
                    </button>
                    <button class="btn btn-secondary btn-lg" id="clearFilesBtn">
                        <i class="fas fa-trash"></i> 清空文件
                    </button>
                </div>
            </div>
        </main>
    </div>

    <script src="/static/js/page.js"></script>
</body>
</html>''',

    'crops.html': '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>作物成熟度分析系统 - 作物库</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link rel="stylesheet" href="/static/css/style.css">
    <link rel="stylesheet" href="/static/css/responsive.css">
    <link rel="stylesheet" href="/static/css/animations.css">
</head>
<body>
    {% include 'navbar.html' %}
    
    <div class="app-container">
        {% include 'sidebar.html' %}
        
        <main class="main-content" id="mainContent">
            <div class="page-header animate-fade-in">
                <h1>作物库</h1>
                <p>管理和查看支持的作物类型及其成熟度标准</p>
            </div>

            <div class="crop-categories animate-fade-in" style="animation-delay: 0.1s">
                <button class="category-btn active" data-category="all">全部</button>
                <button class="category-btn" data-category="solanaceous">茄果类</button>
                <button class="category-btn" data-category="fruit">水果类</button>
            </div>

            <div class="crop-grid" id="cropGrid">
                <div class="crop-card animate-fade-in" style="animation-delay: 0.2s">
                    <div class="crop-header">
                        <span class="crop-icon-large">🫑</span>
                        <span class="crop-badge solanaceous">茄果类</span>
                    </div>
                    <h3 class="crop-name">甜椒</h3>
                    <p class="crop-scientific">Capsicum annuum</p>
                    <p class="crop-desc">果实成熟时呈绿色或红色，富含维生素C，适宜采收期为坐果后30-45天。</p>
                    <div class="crop-standards">
                        <span>参考标准: GB/T 19630-2005</span>
                    </div>
                    <div class="crop-stages">
                        <div class="stage-item">
                            <span class="stage-icon">🌱</span>
                            <span>幼嫩期</span>
                        </div>
                        <div class="stage-item">
                            <span class="stage-icon">🌿</span>
                            <span>成熟期</span>
                        </div>
                        <div class="stage-item">
                            <span class="stage-icon">🥀</span>
                            <span>衰老期</span>
                        </div>
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="pageManager.loadPage('analysis')">选择分析</button>
                </div>

                <div class="crop-card animate-fade-in" style="animation-delay: 0.25s">
                    <div class="crop-header">
                        <span class="crop-icon-large">🥔</span>
                        <span class="crop-badge solanaceous">茄果类</span>
                    </div>
                    <h3 class="crop-name">土豆</h3>
                    <p class="crop-scientific">Solanum tuberosum</p>
                    <p class="crop-desc">块茎作物，叶片繁茂期为最佳检测时机，可判断植株健康状况。</p>
                    <div class="crop-standards">
                        <span>参考标准: GB/T 8321-2012</span>
                    </div>
                    <div class="crop-stages">
                        <div class="stage-item">
                            <span class="stage-icon">🌱</span>
                            <span>幼嫩期</span>
                        </div>
                        <div class="stage-item">
                            <span class="stage-icon">🌿</span>
                            <span>成熟期</span>
                        </div>
                        <div class="stage-item">
                            <span class="stage-icon">🥀</span>
                            <span>衰老期</span>
                        </div>
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="pageManager.loadPage('analysis')">选择分析</button>
                </div>

                <div class="crop-card animate-fade-in" style="animation-delay: 0.3s">
                    <div class="crop-header">
                        <span class="crop-icon-large">🍅</span>
                        <span class="crop-badge solanaceous">茄果类</span>
                    </div>
                    <h3 class="crop-name">番茄</h3>
                    <p class="crop-scientific">Lycopersicon esculentum</p>
                    <p class="crop-desc">果实成熟时颜色从绿转红，叶片健康直接影响果实产量和品质。</p>
                    <div class="crop-standards">
                        <span>参考标准: GB/T 19175-2003</span>
                    </div>
                    <div class="crop-stages">
                        <div class="stage-item">
                            <span class="stage-icon">🌱</span>
                            <span>幼嫩期</span>
                        </div>
                        <div class="stage-item">
                            <span class="stage-icon">🌿</span>
                            <span>成熟期</span>
                        </div>
                        <div class="stage-item">
                            <span class="stage-icon">🥀</span>
                            <span>衰老期</span>
                        </div>
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="pageManager.loadPage('analysis')">选择分析</button>
                </div>

                <div class="crop-card animate-fade-in" style="animation-delay: 0.35s">
                    <div class="crop-header">
                        <span class="crop-icon-large">🍒</span>
                        <span class="crop-badge fruit">水果类</span>
                    </div>
                    <h3 class="crop-name">荔枝</h3>
                    <p class="crop-scientific">Litchi chinensis</p>
                    <p class="crop-desc">常绿果树，叶片状态反映树体营养状况，对果实品质有重要影响。</p>
                    <div class="crop-standards">
                        <span>参考标准: GB/T 18470-2001</span>
                    </div>
                    <div class="crop-stages">
                        <div class="stage-item">
                            <span class="stage-icon">🌱</span>
                            <span>幼嫩期</span>
                        </div>
                        <div class="stage-item">
                            <span class="stage-icon">🌿</span>
                            <span>成熟期</span>
                        </div>
                        <div class="stage-item">
                            <span class="stage-icon">🥀</span>
                            <span>衰老期</span>
                        </div>
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="pageManager.loadPage('analysis')">选择分析</button>
                </div>
            </div>

            <div class="crop-guide animate-fade-in" style="animation-delay: 0.5s">
                <h3><i class="fas fa-info-circle"></i> 作物选择指南</h3>
                <div class="guide-content">
                    <div class="guide-item">
                        <h4>🌱 幼嫩期</h4>
                        <p>叶片鲜嫩，颜色翠绿，适合继续生长，需要充足的水肥管理。</p>
                    </div>
                    <div class="guide-item">
                        <h4>🌿 成熟期</h4>
                        <p>叶片饱满，颜色深绿，达到最佳生理状态，是检测和评估的最佳时机。</p>
                    </div>
                    <div class="guide-item">
                        <h4>🥀 衰老期</h4>
                        <p>叶片黄化干枯，生理功能衰退，建议及时处理或更新植株。</p>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script src="/static/js/page.js"></script>
</body>
</html>''',

    'help.html': '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>作物成熟度分析系统 - 帮助中心</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link rel="stylesheet" href="/static/css/style.css">
    <link rel="stylesheet" href="/static/css/responsive.css">
    <link rel="stylesheet" href="/static/css/animations.css">
</head>
<body>
    {% include 'navbar.html' %}
    
    <div class="app-container">
        {% include 'sidebar.html' %}
        
        <main class="main-content" id="mainContent">
            <div class="page-header animate-fade-in">
                <h1>帮助中心</h1>
                <p>获取系统使用帮助和常见问题解答</p>
            </div>

            <div class="help-container">
                <div class="help-sidebar">
                    <div class="help-section active" data-section="getting-started">
                        <i class="fas fa-play-circle"></i>
                        <span>快速入门</span>
                    </div>
                    <div class="help-section" data-section="analysis">
                        <i class="fas fa-search"></i>
                        <span>分析功能</span>
                    </div>
                    <div class="help-section" data-section="crops">
                        <i class="fas fa-seedling"></i>
                        <span>作物管理</span>
                    </div>
                    <div class="help-section" data-section="reports">
                        <i class="fas fa-file-report"></i>
                        <span>报告导出</span>
                    </div>
                    <div class="help-section" data-section="faq">
                        <i class="fas fa-question-circle"></i>
                        <span>常见问题</span>
                    </div>
                </div>

                <div class="help-content">
                    <div class="help-section-content" id="getting-started">
                        <h2><i class="fas fa-play-circle"></i> 快速入门</h2>
                        <div class="help-step">
                            <div class="step-number">1</div>
                            <div class="step-content">
                                <h3>登录系统</h3>
                                <p>使用您的用户名和密码登录系统。如果还没有账号，请联系管理员获取。</p>
                            </div>
                        </div>
                        <div class="help-step">
                            <div class="step-number">2</div>
                            <div class="step-content">
                                <h3>选择作物类型</h3>
                                <p>在左侧快捷选择或进入作物库选择要检测的作物类型。</p>
                            </div>
                        </div>
                        <div class="help-step">
                            <div class="step-number">3</div>
                            <div class="step-content">
                                <h3>上传图片</h3>
                                <p>进入单图分析或批量分析页面，上传作物叶片图片。</p>
                            </div>
                        </div>
                        <div class="help-step">
                            <div class="step-number">4</div>
                            <div class="step-content">
                                <h3>查看结果</h3>
                                <p>点击分析按钮，等待系统分析完成后查看成熟度检测结果。</p>
                            </div>
                        </div>
                    </div>

                    <div class="help-section-content" id="analysis" style="display: none">
                        <h2><i class="fas fa-search"></i> 分析功能</h2>
                        <div class="help-card">
                            <h3>单图分析</h3>
                            <p>上传单张图片进行成熟度检测，适合快速检测单株作物。</p>
                        </div>
                        <div class="help-card">
                            <h3>批量分析</h3>
                            <p>一次性上传多张图片进行批量检测，提高检测效率。</p>
                        </div>
                        <div class="help-card">
                            <h3>区域分析</h3>
                            <p>对一片区域进行成熟度检测和热力图可视化。</p>
                        </div>
                    </div>

                    <div class="help-section-content" id="crops" style="display: none">
                        <h2><i class="fas fa-seedling"></i> 作物管理</h2>
                        <div class="help-card">
                            <h3>支持的作物</h3>
                            <p>系统目前支持甜椒、土豆、番茄、荔枝四种作物的叶片成熟度检测。</p>
                        </div>
                        <div class="help-card">
                            <h3>成熟度标准</h3>
                            <p>根据叶片颜色、形态等特征判断作物成熟度，分为幼嫩期、成熟期、衰老期三个等级。</p>
                        </div>
                    </div>

                    <div class="help-section-content" id="reports" style="display: none">
                        <h2><i class="fas fa-file-report"></i> 报告导出</h2>
                        <div class="help-card">
                            <h3>导出格式</h3>
                            <p>支持导出PDF和CSV格式的分析报告，方便存档和分享。</p>
                        </div>
                        <div class="help-card">
                            <h3>报告内容</h3>
                            <p>报告包含检测结果、成熟度分布图表、检测时间等详细信息。</p>
                        </div>
                    </div>

                    <div class="help-section-content" id="faq" style="display: none">
                        <h2><i class="fas fa-question-circle"></i> 常见问题</h2>
                        <div class="faq-item">
                            <div class="faq-question">为什么上传图片失败？</div>
                            <div class="faq-answer">请检查图片格式是否正确（支持JPG、PNG、BMP），文件大小是否超过50MB限制。</div>
                        </div>
                        <div class="faq-item">
                            <div class="faq-question">检测结果不准确怎么办？</div>
                            <div class="faq-answer">请确保图片清晰、光照充足，叶片完整可见。可以尝试调整检测精度设置。</div>
                        </div>
                        <div class="faq-item">
                            <div class="faq-question">如何添加新作物？</div>
                            <div class="faq-answer">请联系系统管理员，提供作物样本图片进行模型训练和添加。</div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script src="/static/js/page.js"></script>
</body>
</html>'''
}

def main():
    templates_dir = r'E:\crop-maturity-system\templates'
    
    for filename, content in templates.items():
        file_path = os.path.join(templates_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Restored: {filename}")
    
    print("\nAll templates restored!")

if __name__ == '__main__':
    main()