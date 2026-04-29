from typing import Dict, Any

CROP_STANDARDS: Dict[str, Dict[str, Any]] = {
    'tea': {
        'name': '茶叶',
        'scientific_name': 'Camellia sinensis',
        'reference': 'GB/T 23776-2018 茶叶感官审评方法',
        'maturity_stages': {
            '幼嫩期': {
                'description': '一芽一叶初展至一芽二叶初展',
                'green_ratio_range': (0.45, 1.0),
                'leaf_length_cm': (2.0, 4.0),
                'quality_score': 90,
                'color_code': '#f39c12',
                'icon': '🌱',
                'recommendation': '适制高档绿茶、名优茶',
                'days_to_harvest': 7-14
            },
            '成熟期': {
                'description': '一芽二叶至一芽三叶',
                'green_ratio_range': (0.38, 0.45),
                'leaf_length_cm': (4.0, 6.0),
                'quality_score': 95,
                'color_code': '#27ae60',
                'icon': '🌿',
                'recommendation': '适制大宗绿茶、乌龙茶',
                'days_to_harvest': 0-3
            },
            '过熟期': {
                'description': '一芽三叶以上，叶片开始老化',
                'green_ratio_range': (0.25, 0.38),
                'leaf_length_cm': (6.0, 8.0),
                'quality_score': 75,
                'color_code': '#e67e22',
                'icon': '🍂',
                'recommendation': '适制红茶、边茶',
                'days_to_harvest': -1
            },
            '衰老期': {
                'description': '叶片黄化、变薄，失去采摘价值',
                'green_ratio_range': (0.0, 0.25),
                'leaf_length_cm': (8.0, float('inf')),
                'quality_score': 40,
                'color_code': '#95a5a6',
                'icon': '🥀',
                'recommendation': '不适宜采摘',
                'days_to_harvest': -7
            }
        },
        'optimal_harvest_period': '春季3-4月，秋季9-10月',
        'harvest_interval_days': 7-10
    },
    'tobacco': {
        'name': '烟叶',
        'scientific_name': 'Nicotiana tabacum',
        'reference': 'GB 2635-2018 烤烟',
        'maturity_stages': {
            '幼嫩期': {
                'description': '叶片尚小，颜色浅绿，叶脉不明显',
                'green_ratio_range': (0.50, 1.0),
                'leaf_length_cm': (15.0, 25.0),
                'quality_score': 60,
                'color_code': '#f39c12',
                'icon': '🌱',
                'recommendation': '未成熟，继续生长',
                'days_to_harvest': 14-21
            },
            '成熟期': {
                'description': '叶片适中，颜色深绿，叶脉清晰，叶面有光泽',
                'green_ratio_range': (0.35, 0.50),
                'leaf_length_cm': (25.0, 35.0),
                'quality_score': 95,
                'color_code': '#27ae60',
                'icon': '🌿',
                'recommendation': '最佳采收期，品质最优',
                'days_to_harvest': 0-5
            },
            '过熟期': {
                'description': '叶片开始变黄，叶尖下垂，叶缘卷曲',
                'green_ratio_range': (0.20, 0.35),
                'leaf_length_cm': (35.0, 45.0),
                'quality_score': 70,
                'color_code': '#e67e22',
                'icon': '🍂',
                'recommendation': '尽快采收，品质下降',
                'days_to_harvest': -3
            },
            '衰老期': {
                'description': '叶片严重黄化、干枯，失去商业价值',
                'green_ratio_range': (0.0, 0.20),
                'leaf_length_cm': (45.0, float('inf')),
                'quality_score': 30,
                'color_code': '#95a5a6',
                'icon': '🥀',
                'recommendation': '无采收价值',
                'days_to_harvest': -10
            }
        },
        'optimal_harvest_period': '移栽后60-75天',
        'harvest_interval_days': 3-5
    },
    'mulberry': {
        'name': '桑叶',
        'scientific_name': 'Morus alba',
        'reference': 'NY/T 1187-2006 桑树栽培技术规程',
        'maturity_stages': {
            '幼嫩期': {
                'description': '新梢顶部2-3片叶，颜色嫩绿',
                'green_ratio_range': (0.48, 1.0),
                'leaf_length_cm': (3.0, 6.0),
                'quality_score': 85,
                'color_code': '#f39c12',
                'icon': '🌱',
                'recommendation': '适用于小蚕饲养',
                'days_to_harvest': 5-7
            },
            '成熟期': {
                'description': '叶片充分展开，颜色深绿，质地柔软',
                'green_ratio_range': (0.40, 0.48),
                'leaf_length_cm': (6.0, 12.0),
                'quality_score': 95,
                'color_code': '#27ae60',
                'icon': '🌿',
                'recommendation': '适用于大蚕饲养，营养最佳',
                'days_to_harvest': 0-3
            },
            '过熟期': {
                'description': '叶片开始老化，颜色变浅，叶缘略有卷曲',
                'green_ratio_range': (0.28, 0.40),
                'leaf_length_cm': (12.0, 18.0),
                'quality_score': 70,
                'color_code': '#e67e22',
                'icon': '🍂',
                'recommendation': '可用于饲料或肥料',
                'days_to_harvest': -3
            },
            '衰老期': {
                'description': '叶片黄化、干枯、易碎',
                'green_ratio_range': (0.0, 0.28),
                'leaf_length_cm': (18.0, float('inf')),
                'quality_score': 35,
                'color_code': '#95a5a6',
                'icon': '🥀',
                'recommendation': '无饲养价值',
                'days_to_harvest': -7
            }
        },
        'optimal_harvest_period': '春蚕期4-5月，秋蚕期9-10月',
        'harvest_interval_days': 5-7
    },
    'lettuce': {
        'name': '生菜',
        'scientific_name': 'Lactuca sativa',
        'reference': 'GB/T 18407.1-2001 农产品安全质量 无公害蔬菜安全要求',
        'maturity_stages': {
            '幼嫩期': {
                'description': '叶片数少，株型小，颜色浅绿',
                'green_ratio_range': (0.55, 1.0),
                'plant_diameter_cm': (8.0, 15.0),
                'quality_score': 70,
                'color_code': '#f39c12',
                'icon': '🌱',
                'recommendation': '可采收幼苗，口感鲜嫩',
                'days_to_harvest': 7-14
            },
            '成熟期': {
                'description': '叶片充分展开，株型适中，颜色深绿，心叶开始包裹',
                'green_ratio_range': (0.42, 0.55),
                'plant_diameter_cm': (15.0, 25.0),
                'quality_score': 95,
                'color_code': '#27ae60',
                'icon': '🌿',
                'recommendation': '最佳采收期，商品价值最高',
                'days_to_harvest': 0-5
            },
            '过熟期': {
                'description': '叶片开始老化，叶缘发黄，抽薹初期',
                'green_ratio_range': (0.28, 0.42),
                'plant_diameter_cm': (25.0, 35.0),
                'quality_score': 65,
                'color_code': '#e67e22',
                'icon': '🍂',
                'recommendation': '尽快采收，口感变差',
                'days_to_harvest': -3
            },
            '衰老期': {
                'description': '严重抽薹，叶片黄化干枯，失去食用价值',
                'green_ratio_range': (0.0, 0.28),
                'plant_diameter_cm': (35.0, float('inf')),
                'quality_score': 25,
                'color_code': '#95a5a6',
                'icon': '🥀',
                'recommendation': '无食用价值',
                'days_to_harvest': -10
            }
        },
        'optimal_harvest_period': '播种后40-60天',
        'harvest_interval_days': 3-5
    },
    'spinach': {
        'name': '菠菜',
        'scientific_name': 'Spinacia oleracea',
        'reference': 'NY/T 5008-2016 无公害食品 绿叶蔬菜类',
        'maturity_stages': {
            '幼嫩期': {
                'description': '真叶3-4片，植株矮小',
                'green_ratio_range': (0.52, 1.0),
                'plant_height_cm': (5.0, 12.0),
                'quality_score': 75,
                'color_code': '#f39c12',
                'icon': '🌱',
                'recommendation': '可采收嫩菠菜',
                'days_to_harvest': 7-10
            },
            '成熟期': {
                'description': '真叶5-7片，叶片肥厚，颜色深绿',
                'green_ratio_range': (0.40, 0.52),
                'plant_height_cm': (12.0, 22.0),
                'quality_score': 95,
                'color_code': '#27ae60',
                'icon': '🌿',
                'recommendation': '最佳采收期，营养丰富',
                'days_to_harvest': 0-3
            },
            '过熟期': {
                'description': '叶片开始老化，叶柄变长，颜色变浅',
                'green_ratio_range': (0.25, 0.40),
                'plant_height_cm': (22.0, 32.0),
                'quality_score': 65,
                'color_code': '#e67e22',
                'icon': '🍂',
                'recommendation': '尽快采收，纤维增多',
                'days_to_harvest': -3
            },
            '衰老期': {
                'description': '抽薹开花，叶片黄化干枯',
                'green_ratio_range': (0.0, 0.25),
                'plant_height_cm': (32.0, float('inf')),
                'quality_score': 20,
                'color_code': '#95a5a6',
                'icon': '🥀',
                'recommendation': '失去食用价值',
                'days_to_harvest': -7
            }
        },
        'optimal_harvest_period': '播种后30-45天',
        'harvest_interval_days': 3-4
    },
    'celery': {
        'name': '芹菜',
        'scientific_name': 'Apium graveolens',
        'reference': 'NY/T 5008-2016 无公害食品 绿叶蔬菜类',
        'maturity_stages': {
            '幼嫩期': {
                'description': '植株较小，叶柄细，叶片嫩',
                'green_ratio_range': (0.48, 1.0),
                'plant_height_cm': (15.0, 25.0),
                'quality_score': 70,
                'color_code': '#f39c12',
                'icon': '🌱',
                'recommendation': '可采收嫩芹菜',
                'days_to_harvest': 10-15
            },
            '成熟期': {
                'description': '叶柄粗壮，颜色翠绿，植株挺拔',
                'green_ratio_range': (0.38, 0.48),
                'plant_height_cm': (25.0, 40.0),
                'quality_score': 95,
                'color_code': '#27ae60',
                'icon': '🌿',
                'recommendation': '最佳采收期，品质最优',
                'days_to_harvest': 0-5
            },
            '过熟期': {
                'description': '叶柄开始纤维化，颜色变浅，基部开裂',
                'green_ratio_range': (0.22, 0.38),
                'plant_height_cm': (40.0, 55.0),
                'quality_score': 60,
                'color_code': '#e67e22',
                'icon': '🍂',
                'recommendation': '尽快采收，口感变差',
                'days_to_harvest': -3
            },
            '衰老期': {
                'description': '严重老化，叶片黄化，空心',
                'green_ratio_range': (0.0, 0.22),
                'plant_height_cm': (55.0, float('inf')),
                'quality_score': 25,
                'color_code': '#95a5a6',
                'icon': '🥀',
                'recommendation': '失去商品价值',
                'days_to_harvest': -10
            }
        },
        'optimal_harvest_period': '定植后60-90天',
        'harvest_interval_days': 5-7
    }
}

def get_crop_standards(crop_type: str) -> Dict[str, Any]:
    return CROP_STANDARDS.get(crop_type, CROP_STANDARDS.get('tea'))

def get_maturity_stage(crop_type: str, green_ratio: float) -> Dict[str, Any]:
    standards = get_crop_standards(crop_type)
    for stage, criteria in standards['maturity_stages'].items():
        min_ratio, max_ratio = criteria['green_ratio_range']
        if min_ratio <= green_ratio <= max_ratio:
            return {
                'stage': stage,
                **criteria
            }
    return standards['maturity_stages']['衰老期']

def get_all_crop_types() -> list:
    return list(CROP_STANDARDS.keys())

def get_maturity_color(stage: str) -> str:
    color_map = {
        '幼嫩期': '#f39c12',
        '成熟期': '#27ae60',
        '过熟期': '#e67e22',
        '衰老期': '#95a5a6'
    }
    return color_map.get(stage, '#27ae60')

def get_maturity_icon(stage: str) -> str:
    icon_map = {
        '幼嫩期': '🌱',
        '成熟期': '🌿',
        '过熟期': '🍂',
        '衰老期': '🥀'
    }
    return icon_map.get(stage, '🌿')