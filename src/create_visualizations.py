"""
Создание всех графиков для финальной работы по курсу
Генерация визуализаций для A/B тестирования акции на премиум броню
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Настройка стиля графиков
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.grid'] = True

class ABTestVisualizer:
    def __init__(self, results_data):
        """
        Инициализация класса для создания визуализаций
        
        Args:
            results_data: Словарь с результатами анализа
        """
        self.results = results_data
        self.colors = {
            'control': '#3498db',  # Синий
            'test': '#e74c3c',     # Красный  
            'improvement': '#27ae60', # Зелёный
            'neutral': '#95a5a6'   # Серый
        }
        
    def create_metrics_comparison(self):
        """График 1: Сравнение основных метрик между группами"""
        
        # Данные для графика
        metrics = ['ARPU', 'ARPPU', 'Траты валюты']
        control_values = [5.8295, 5.8311, 5800.71]
        test_values = [6.1622, 6.1631, 6229.57]
        improvements = [5.71, 5.69, 7.39]
        
        # Нормализация трат валюты для лучшей визуализации
        control_values_norm = [5.8295, 5.8311, 5.80071]  # Валюта /1000
        test_values_norm = [6.1622, 6.1631, 6.22957]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # График сравнения средних значений
        x = np.arange(len(metrics))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, control_values_norm, width, 
                       label='Контрольная группа', color=self.colors['control'], alpha=0.8)
        bars2 = ax1.bar(x + width/2, test_values_norm, width,
                       label='Тестовая группа', color=self.colors['test'], alpha=0.8)
        
        ax1.set_xlabel('Метрики')
        ax1.set_ylabel('Значение (USD / тыс. монет)')
        ax1.set_title('Сравнение ключевых метрик между группами')
        ax1.set_xticks(x)
        ax1.set_xticklabels(metrics)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Добавление значений на столбцы
        for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
            height1 = bar1.get_height()
            height2 = bar2.get_height()
            
            if i < 2:  # ARPU и ARPPU
                ax1.text(bar1.get_x() + bar1.get_width()/2., height1 + 0.05,
                        f'${control_values[i]:.2f}', ha='center', va='bottom')
                ax1.text(bar2.get_x() + bar2.get_width()/2., height2 + 0.05,
                        f'${test_values[i]:.2f}', ha='center', va='bottom')
            else:  # Траты валюты
                ax1.text(bar1.get_x() + bar1.get_width()/2., height1 + 0.05,
                        f'{control_values[i]:.0f}', ha='center', va='bottom')
                ax1.text(bar2.get_x() + bar2.get_width()/2., height2 + 0.05,
                        f'{test_values[i]:.0f}', ha='center', va='bottom')
        
        # График улучшений в процентах
        bars3 = ax2.bar(metrics, improvements, color=self.colors['improvement'], alpha=0.8)
        ax2.set_xlabel('Метрики')
        ax2.set_ylabel('Улучшение (%)')
        ax2.set_title('Процентное улучшение в тестовой группе')
        ax2.grid(True, alpha=0.3)
        
        # Добавление значений на столбцы
        for bar, imp in zip(bars3, improvements):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'+{imp:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/Users/user/AB_test/visualizations/01_metrics_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()  # Close instead of show to avoid display issues
        
    def create_confidence_intervals(self):
        """График 2: Доверительные интервалы для всех метрик"""
        
        # Данные доверительных интервалов
        metrics_data = {
            'ARPU': {
                'control': {'mean': 5.8295, 'ci_lower': 5.8289, 'ci_upper': 5.8301},
                'test': {'mean': 6.1622, 'ci_lower': 6.1616, 'ci_upper': 6.1628}
            },
            'ARPPU': {
                'control': {'mean': 5.8311, 'ci_lower': 5.8305, 'ci_upper': 5.8317},
                'test': {'mean': 6.1631, 'ci_lower': 6.1625, 'ci_upper': 6.1637}
            },
            'Траты валюты': {
                'control': {'mean': 5800.71, 'ci_lower': 5799.44, 'ci_upper': 5801.98},
                'test': {'mean': 6229.57, 'ci_lower': 6228.23, 'ci_upper': 6230.91}
            }
        }
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        for i, (metric, data) in enumerate(metrics_data.items()):
            ax = axes[i]
            
            # Данные для графика
            groups = ['Control', 'Test']
            means = [data['control']['mean'], data['test']['mean']]
            ci_lowers = [data['control']['ci_lower'], data['test']['ci_lower']]
            ci_uppers = [data['control']['ci_upper'], data['test']['ci_upper']]
            
            # Расчёт error bars
            errors_lower = [means[j] - ci_lowers[j] for j in range(2)]
            errors_upper = [ci_uppers[j] - means[j] for j in range(2)]
            
            # График с error bars
            colors = [self.colors['control'], self.colors['test']]
            bars = ax.bar(groups, means, yerr=[errors_lower, errors_upper], 
                         capsize=10, color=colors, alpha=0.8, 
                         error_kw={'linewidth': 2, 'capthick': 2})
            
            ax.set_title(f'{metric}\n95% Доверительные интервалы')
            ax.set_ylabel('USD' if 'ARPU' in metric else 'Монеты')
            ax.grid(True, alpha=0.3)
            
            # Добавление значений
            for j, (bar, mean, ci_low, ci_up) in enumerate(zip(bars, means, ci_lowers, ci_uppers)):
                height = bar.get_height()
                
                if 'валюта' in metric.lower():
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                           f'{mean:.0f}\n[{ci_low:.0f}, {ci_up:.0f}]',
                           ha='center', va='bottom', fontsize=10)
                else:
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                           f'${mean:.4f}\n[${ci_low:.4f}, ${ci_up:.4f}]',
                           ha='center', va='bottom', fontsize=10)
            
            # Проверка пересечения интервалов
            control_upper = data['control']['ci_upper']
            test_lower = data['test']['ci_lower']
            
            if control_upper < test_lower:
                ax.text(0.5, 0.95, '✅ Интервалы НЕ пересекаются\n(статистически значимо)', 
                       transform=ax.transAxes, ha='center', va='top',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7))
        
        plt.tight_layout()
        plt.savefig('/Users/user/AB_test/visualizations/02_confidence_intervals.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_platform_analysis(self):
        """График 3: Анализ ARPU по платформам"""
        
        # Данные по платформам
        platform_data = {
            'PC': {'control': 5.6462, 'test': 6.2690, 'improvement': 11.02},
            'PS4': {'control': 5.7376, 'test': 6.0848, 'improvement': 6.05},
            'Xbox': {'control': 6.1035, 'test': 6.1328, 'improvement': 0.48}
        }
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # График 1: ARPU по платформам и группам
        platforms = list(platform_data.keys())
        control_values = [platform_data[p]['control'] for p in platforms]
        test_values = [platform_data[p]['test'] for p in platforms]
        
        x = np.arange(len(platforms))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, control_values, width, 
                       label='Контрольная группа', color=self.colors['control'], alpha=0.8)
        bars2 = ax1.bar(x + width/2, test_values, width,
                       label='Тестовая группа', color=self.colors['test'], alpha=0.8)
        
        ax1.set_xlabel('Игровые платформы')
        ax1.set_ylabel('ARPU (USD)')
        ax1.set_title('ARPU по платформам и группам')
        ax1.set_xticks(x)
        ax1.set_xticklabels(platforms)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Добавление значений на столбцы
        for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
            height1 = bar1.get_height()
            height2 = bar2.get_height()
            ax1.text(bar1.get_x() + bar1.get_width()/2., height1 + 0.02,
                    f'${control_values[i]:.2f}', ha='center', va='bottom')
            ax1.text(bar2.get_x() + bar2.get_width()/2., height2 + 0.02,
                    f'${test_values[i]:.2f}', ha='center', va='bottom')
        
        # График 2: Процентное улучшение по платформам
        improvements = [platform_data[p]['improvement'] for p in platforms]
        colors_improvement = [self.colors['improvement'] if imp > 5 else self.colors['neutral'] for imp in improvements]
        
        bars3 = ax2.bar(platforms, improvements, color=colors_improvement, alpha=0.8)
        ax2.set_xlabel('Игровые платформы')
        ax2.set_ylabel('Улучшение ARPU (%)')
        ax2.set_title('Эффективность акции по платформам')
        ax2.grid(True, alpha=0.3)
        
        # Добавление значений и интерпретации
        for i, (bar, imp) in enumerate(zip(bars3, improvements)):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                    f'+{imp:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            # Добавление категории эффективности
            if imp > 10:
                category = "Высокая"
            elif imp > 5:
                category = "Средняя"
            else:
                category = "Низкая"
                
            ax2.text(bar.get_x() + bar.get_width()/2., -0.5,
                    category, ha='center', va='top', fontsize=10, style='italic')
        
        plt.tight_layout()
        plt.savefig('/Users/user/AB_test/visualizations/03_platform_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_statistical_significance(self):
        """График 4: Визуализация статистической значимости"""
        
        # Данные статистических тестов
        test_results = {
            'ARPU': {'t_stat': -258.37, 'p_value': 1e-7, 'cohens_d': -0.179},
            'ARPPU': {'t_stat': -257.99, 'p_value': 1e-7, 'cohens_d': -0.179},
            'Траты валюты': {'t_stat': -456.73, 'p_value': 1e-7, 'cohens_d': -0.312}
        }
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # График 1: t-статистики
        metrics = list(test_results.keys())
        t_stats = [abs(test_results[m]['t_stat']) for m in metrics]
        
        bars1 = ax1.bar(metrics, t_stats, color=self.colors['test'], alpha=0.8)
        ax1.set_xlabel('Метрики')
        ax1.set_ylabel('|t-статистика|')
        ax1.set_title('Статистическая значимость (t-тесты)')
        ax1.grid(True, alpha=0.3)
        
        # Линия критического значения t (α=0.05, df≈∞)
        ax1.axhline(y=1.96, color='red', linestyle='--', alpha=0.7, 
                   label='Критическое значение (α=0.05)')
        ax1.legend()
        
        # Добавление значений
        for bar, t_stat in zip(bars1, t_stats):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 5,
                    f'{t_stat:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # График 2: Размеры эффекта (Cohen's d)
        cohens_d_values = [abs(test_results[m]['cohens_d']) for m in metrics]
        
        # Цвета в зависимости от размера эффекта
        colors_effect = []
        for d in cohens_d_values:
            if d < 0.2:
                colors_effect.append('#f39c12')  # Оранжевый - очень малый
            elif d < 0.5:
                colors_effect.append('#e67e22')  # Тёмно-оранжевый - малый
            elif d < 0.8:
                colors_effect.append('#27ae60')  # Зелёный - средний
            else:
                colors_effect.append('#c0392b')  # Красный - большой
        
        bars2 = ax2.bar(metrics, cohens_d_values, color=colors_effect, alpha=0.8)
        ax2.set_xlabel('Метрики')
        ax2.set_ylabel("Cohen's d")
        ax2.set_title('Размер эффекта (практическая значимость)')
        ax2.grid(True, alpha=0.3)
        
        # Линии границ размера эффекта
        ax2.axhline(y=0.2, color='gray', linestyle=':', alpha=0.7, label='Малый эффект')
        ax2.axhline(y=0.5, color='gray', linestyle='--', alpha=0.7, label='Средний эффект')
        ax2.axhline(y=0.8, color='gray', linestyle='-', alpha=0.7, label='Большой эффект')
        ax2.legend()
        
        # Добавление значений и интерпретации
        effect_labels = ['Малый', 'Малый', 'Малый']
        for bar, d, label in zip(bars2, cohens_d_values, effect_labels):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{d:.3f}\n({label})', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig('/Users/user/AB_test/visualizations/04_statistical_significance.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_revenue_projection(self):
        """График 5: Проекция увеличения дохода"""
        
        # Данные проекции
        base_daily_revenue = 50.3  # Миллионы USD
        improvement_daily = 2.87   # Миллионы USD
        
        periods = ['Дневной', 'Недельный', 'Месячный', 'Квартальный', 'Годовой']
        multipliers = [1, 7, 30, 90, 365]
        
        base_revenues = [base_daily_revenue * m for m in multipliers]
        improvements = [improvement_daily * m for m in multipliers]
        new_revenues = [base + imp for base, imp in zip(base_revenues, improvements)]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
        
        # График 1: Абсолютные значения доходов
        x = np.arange(len(periods))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, base_revenues, width, 
                       label='Текущий доход', color=self.colors['control'], alpha=0.8)
        bars2 = ax1.bar(x + width/2, new_revenues, width,
                       label='Доход с акцией', color=self.colors['test'], alpha=0.8)
        
        ax1.set_xlabel('Период')
        ax1.set_ylabel('Доход (млн USD)')
        ax1.set_title('Проекция увеличения дохода от внедрения акции')
        ax1.set_xticks(x)
        ax1.set_xticklabels(periods)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Добавление значений
        for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
            height1 = bar1.get_height()
            height2 = bar2.get_height()
            
            # Форматирование в зависимости от размера
            if height1 >= 1000:
                ax1.text(bar1.get_x() + bar1.get_width()/2., height1 + 50,
                        f'${height1/1000:.1f}Б', ha='center', va='bottom')
                ax1.text(bar2.get_x() + bar2.get_width()/2., height2 + 50,
                        f'${height2/1000:.1f}Б', ha='center', va='bottom')
            else:
                ax1.text(bar1.get_x() + bar1.get_width()/2., height1 + 5,
                        f'${height1:.0f}М', ha='center', va='bottom')
                ax1.text(bar2.get_x() + bar2.get_width()/2., height2 + 5,
                        f'${height2:.0f}М', ha='center', va='bottom')
        
        # График 2: Дополнительный доход от акции
        bars3 = ax2.bar(periods, improvements, color=self.colors['improvement'], alpha=0.8)
        ax2.set_xlabel('Период')
        ax2.set_ylabel('Дополнительный доход (млн USD)')
        ax2.set_title('Дополнительный доход от акции (+5.71% ARPU)')
        ax2.grid(True, alpha=0.3)
        
        # Добавление значений
        for bar, imp in zip(bars3, improvements):
            height = bar.get_height()
            if height >= 1000:
                ax2.text(bar.get_x() + bar.get_width()/2., height + 20,
                        f'+${height/1000:.2f}Б', ha='center', va='bottom', 
                        fontweight='bold', color='darkgreen')
            else:
                ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'+${height:.1f}М', ha='center', va='bottom', 
                        fontweight='bold', color='darkgreen')
        
        plt.tight_layout()
        plt.savefig('/Users/user/AB_test/visualizations/05_revenue_projection.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_data_quality_summary(self):
        """График 6: Сводка по качеству данных и очистке"""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # График 1: Процесс очистки данных
        stages = ['Исходные\nданные', 'После удаления\nчитеров', 'После удаления\nвыбросов']
        counts = [8640000, 8637176, 8634408]
        removed = [0, 2824, 2768]
        
        bars1 = ax1.bar(stages, counts, color=[self.colors['neutral'], 
                       self.colors['control'], self.colors['improvement']], alpha=0.8)
        ax1.set_ylabel('Количество игроков')
        ax1.set_title('Этапы очистки данных')
        ax1.grid(True, alpha=0.3)
        
        # Добавление значений
        for i, (bar, count, rem) in enumerate(zip(bars1, counts, removed)):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 20000,
                    f'{count:,}', ha='center', va='bottom', fontweight='bold')
            if rem > 0:
                ax1.text(bar.get_x() + bar.get_width()/2., height - 100000,
                        f'-{rem:,}', ha='center', va='center', color='red')
        
        # График 2: Распределение по группам
        groups = ['Контрольная\nгруппа', 'Тестовая\nгруппа']
        group_counts = [4319928, 4314480]
        group_percentages = [50.0, 50.0]
        
        bars2 = ax2.bar(groups, group_counts, 
                       color=[self.colors['control'], self.colors['test']], alpha=0.8)
        ax2.set_ylabel('Количество игроков')
        ax2.set_title('Распределение по группам A/B теста')
        ax2.grid(True, alpha=0.3)
        
        for bar, count, pct in zip(bars2, group_counts, group_percentages):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 20000,
                    f'{count:,}\n({pct:.1f}%)', ha='center', va='bottom', fontweight='bold')
        
        # График 3: Распределение по платформам
        platforms = ['PC', 'PS4', 'Xbox']
        platform_counts = [2876408, 2873744, 2884256]
        platform_colors = ['#3498db', '#e74c3c', '#2ecc71']
        
        wedges, texts, autotexts = ax3.pie(platform_counts, labels=platforms, 
                                          colors=platform_colors, autopct='%1.1f%%',
                                          startangle=90)
        ax3.set_title('Распределение игроков по платформам')
        
        # График 4: Качество данных
        quality_metrics = ['Полнота\nданных', 'Корректность\nгрупп', 'Чистота\nот читеров']
        quality_scores = [99.935, 100.0, 99.996]
        
        bars4 = ax4.bar(quality_metrics, quality_scores, 
                       color=self.colors['improvement'], alpha=0.8)
        ax4.set_ylabel('Процент качества (%)')
        ax4.set_title('Показатели качества данных')
        ax4.set_ylim(99.5, 100.1)
        ax4.grid(True, alpha=0.3)
        
        for bar, score in zip(bars4, quality_scores):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{score:.2f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/Users/user/AB_test/visualizations/06_data_quality.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_interactive_dashboard(self):
        """График 7: Интерактивный dashboard (Plotly)"""
        
        # Создание subplot dashboard
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Сравнение метрик', 'ARPU по платформам', 
                          'Доверительные интервалы', 'Проекция дохода'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # График 1: Сравнение метрик
        metrics = ['ARPU', 'ARPPU', 'Траты валюты (тыс.)']
        control_vals = [5.83, 5.83, 5.80]
        test_vals = [6.16, 6.16, 6.23]
        
        fig.add_trace(
            go.Bar(name='Контроль', x=metrics, y=control_vals, 
                   marker_color='#3498db', opacity=0.8),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(name='Тест', x=metrics, y=test_vals, 
                   marker_color='#e74c3c', opacity=0.8),
            row=1, col=1
        )
        
        # График 2: ARPU по платформам
        platforms = ['PC', 'PS4', 'Xbox']
        platform_control = [5.65, 5.74, 6.10]
        platform_test = [6.27, 6.08, 6.13]
        
        fig.add_trace(
            go.Bar(name='Контроль (платформы)', x=platforms, y=platform_control,
                   marker_color='#3498db', opacity=0.8, showlegend=False),
            row=1, col=2
        )
        fig.add_trace(
            go.Bar(name='Тест (платформы)', x=platforms, y=platform_test,
                   marker_color='#e74c3c', opacity=0.8, showlegend=False),
            row=1, col=2
        )
        
        # График 3: Доверительные интервалы ARPU
        groups = ['Контроль', 'Тест']
        means = [5.8295, 6.1622]
        errors = [0.0006, 0.0006]
        
        fig.add_trace(
            go.Bar(name='ARPU с ДИ', x=groups, y=means,
                   error_y=dict(type='data', array=errors, visible=True),
                   marker_color=['#3498db', '#e74c3c'], opacity=0.8, showlegend=False),
            row=2, col=1
        )
        
        # График 4: Проекция дохода
        periods = ['День', 'Месяц', 'Год']
        improvements = [2.87, 86.1, 1050]
        
        fig.add_trace(
            go.Bar(name='Доп. доход', x=periods, y=improvements,
                   marker_color='#27ae60', opacity=0.8, showlegend=False),
            row=2, col=2
        )
        
        # Настройка layout
        fig.update_layout(
            title_text="A/B Тест: Интерактивный Dashboard",
            title_x=0.5,
            height=800,
            showlegend=True
        )
        
        # Сохранение интерактивного графика
        fig.write_html("/Users/user/AB_test/visualizations/07_interactive_dashboard.html")
        print("📱 Интерактивный dashboard сохранён")
        
    def generate_all_visualizations(self):
        """Создание всех графиков для отчёта"""
        
        import os
        os.makedirs('/Users/user/AB_test/visualizations', exist_ok=True)
        
        print("🎨 Создание визуализаций для финальной работы...")
        print("=" * 60)
        
        print("📊 График 1: Сравнение основных метрик...")
        self.create_metrics_comparison()
        
        print("📈 График 2: Доверительные интервалы...")
        self.create_confidence_intervals()
        
        print("🎮 График 3: Анализ по платформам...")
        self.create_platform_analysis()
        
        print("🔬 График 4: Статистическая значимость...")
        self.create_statistical_significance()
        
        print("💰 График 5: Проекция дохода...")
        self.create_revenue_projection()
        
        print("🧹 График 6: Качество данных...")
        self.create_data_quality_summary()
        
        print("📱 График 7: Интерактивный dashboard...")
        self.create_interactive_dashboard()
        
        print("\n✅ Все графики созданы и сохранены в папку 'visualizations/'")
        print("📁 Файлы готовы для включения в финальную работу:")
        print("   • 01_metrics_comparison.png")
        print("   • 02_confidence_intervals.png") 
        print("   • 03_platform_analysis.png")
        print("   • 04_statistical_significance.png")
        print("   • 05_revenue_projection.png")
        print("   • 06_data_quality.png")
        print("   • 07_interactive_dashboard.html")

def main():
    """Основная функция для запуска создания графиков"""
    
    # Моковые данные результатов (в реальном проекте загружались бы из анализа)
    results_data = {
        'arpu': {'control': 5.8295, 'test': 6.1622, 'improvement': 5.71},
        'arppu': {'control': 5.8311, 'test': 6.1631, 'improvement': 5.69},
        'cash': {'control': 5800.71, 'test': 6229.57, 'improvement': 7.39}
    }
    
    # Создание визуализатора и генерация всех графиков
    visualizer = ABTestVisualizer(results_data)
    visualizer.generate_all_visualizations()

if __name__ == "__main__":
    main() 