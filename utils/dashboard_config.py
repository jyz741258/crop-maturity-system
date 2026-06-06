import json
import os

class DashboardConfig:
    DEFAULT_CONFIG = {
        'theme': 'light',
        'layout': 'grid',
        'refresh_interval': 300,
        'show_stats': True,
        'show_charts': True,
        'show_recent': True,
        'show_crop_distribution': True,
        'chart_types': ['pie', 'line', 'bar', 'radar'],
        'stats_cards': [
            {'id': 'total', 'label': '今日检测总数', 'visible': True},
            {'id': 'mature_count', 'label': '成熟作物数', 'visible': True},
            {'id': 'rate', 'label': '整体成熟率', 'visible': True},
            {'id': 'avg_time', 'label': '平均分析时长', 'visible': True}
        ],
        'charts': [
            {'id': 'maturityPie', 'type': 'pie', 'title': '成熟度分布', 'visible': True, 'size': 'medium'},
            {'id': 'trendChart', 'type': 'line', 'title': '检测趋势', 'visible': True, 'size': 'medium'},
            {'id': 'qualityBar', 'type': 'bar', 'title': '品质评分分布', 'visible': True, 'size': 'medium'},
            {'id': 'radarChart', 'type': 'radar', 'title': '特征分析', 'visible': True, 'size': 'medium'},
            {'id': 'areaChart', 'type': 'area', 'title': '趋势面积图', 'visible': False, 'size': 'large'},
            {'id': 'scatterChart', 'type': 'scatter', 'title': '散点分布图', 'visible': False, 'size': 'large'},
            {'id': 'heatmapChart', 'type': 'heatmap', 'title': '地块热力图', 'visible': False, 'size': 'large'}
        ],
        'crop_types': ['tea', 'tobacco', 'mulberry', 'lettuce'],
        'data_range': '7days',
        'language': 'zh-CN'
    }

    def __init__(self, config_file='dashboard_config.json'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()

    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    def update_config(self, updates):
        self.config.update(updates)
        self.save_config()

    def reset_to_default(self):
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()

    def toggle_stat_card(self, card_id):
        for card in self.config['stats_cards']:
            if card['id'] == card_id:
                card['visible'] = not card['visible']
                self.save_config()
                return True
        return False

    def toggle_chart(self, chart_id):
        for chart in self.config['charts']:
            if chart['id'] == chart_id:
                chart['visible'] = not chart['visible']
                self.save_config()
                return True
        return False

    def set_chart_size(self, chart_id, size):
        for chart in self.config['charts']:
            if chart['id'] == chart_id:
                chart['size'] = size
                self.save_config()
                return True
        return False

    def set_refresh_interval(self, interval):
        self.config['refresh_interval'] = interval
        self.save_config()

    def set_theme(self, theme):
        self.config['theme'] = theme
        self.save_config()

    def get_visible_stats(self):
        return [card for card in self.config['stats_cards'] if card['visible']]

    def get_visible_charts(self):
        return [chart for chart in self.config['charts'] if chart['visible']]

    def get_layout(self):
        return self.config.get('layout', 'grid')

    def get_theme(self):
        return self.config.get('theme', 'light')

    def to_dict(self):
        return self.config.copy()

    def export_config(self):
        return json.dumps(self.config, ensure_ascii=False, indent=2)

    def import_config(self, config_json):
        try:
            new_config = json.loads(config_json)
            self.config = new_config
            self.save_config()
            return True
        except:
            return False