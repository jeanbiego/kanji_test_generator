"""
統計機能モジュール

学習進捗や問題の正誤率などの統計情報を計算・可視化する。
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from src.modules.models import Problem, Attempt
from src.modules.storage import ProblemStorage, AttemptStorage
from src.modules.logger import app_logger


class StatisticsCalculator:
    """統計計算エンジン"""
    
    def __init__(self):
        self.problem_storage = ProblemStorage()
        self.attempt_storage = AttemptStorage()
    
    def calculate_problem_statistics(self, problems: List[Problem]) -> Dict[str, Any]:
        """問題別統計を計算"""
        try:
            attempts = self.attempt_storage.load_attempts()
            problem_stats = {}
            
            for problem in problems:
                problem_attempts = [a for a in attempts if a.problem_id == problem.id]
                
                if problem_attempts:
                    correct_count = sum(1 for a in problem_attempts if a.is_correct)
                    total_count = len(problem_attempts)
                    accuracy = (correct_count / total_count) * 100
                    
                    # 最新の試行日
                    latest_attempt = max(problem_attempts, key=lambda x: x.timestamp)
                    last_attempted = latest_attempt.timestamp
                    
                    # 間違いの種類の分布
                    mistake_distribution = defaultdict(int)
                    for attempt in problem_attempts:
                        if not attempt.is_correct:
                            mistake_distribution[attempt.mistake_type] += 1
                    
                    problem_stats[problem.id] = {
                        'problem': problem,
                        'correct_count': correct_count,
                        'total_count': total_count,
                        'accuracy': accuracy,
                        'last_attempted': last_attempted,
                        'mistake_distribution': dict(mistake_distribution)
                    }
                else:
                    problem_stats[problem.id] = {
                        'problem': problem,
                        'correct_count': 0,
                        'total_count': 0,
                        'accuracy': 0.0,
                        'last_attempted': None,
                        'mistake_distribution': {}
                    }
            
            app_logger.info(f"問題別統計計算完了: {len(problems)}件")
            return problem_stats
            
        except Exception as e:
            app_logger.error(f"問題別統計計算中にエラーが発生しました: {e}")
            return {}
    
    def calculate_daily_statistics(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]:
        """日別統計を計算"""
        try:
            attempts = self.attempt_storage.load_attempts()
            
            if not attempts:
                return {
                    'daily_data': [],
                    'total_attempts': 0,
                    'total_correct': 0,
                    'overall_accuracy': 0.0
                }
            
            # 日付範囲でフィルタリング
            if start_date:
                attempts = [a for a in attempts if a.timestamp.date() >= start_date]
            if end_date:
                attempts = [a for a in attempts if a.timestamp.date() <= end_date]
            
            # 日別にグループ化
            daily_data = defaultdict(lambda: {'attempts': 0, 'correct': 0})
            
            for attempt in attempts:
                day = attempt.timestamp.date()
                daily_data[day]['attempts'] += 1
                if attempt.is_correct:
                    daily_data[day]['correct'] += 1
            
            # データを整理
            daily_stats = []
            for day in sorted(daily_data.keys()):
                day_data = daily_data[day]
                accuracy = (day_data['correct'] / day_data['attempts']) * 100 if day_data['attempts'] > 0 else 0
                
                daily_stats.append({
                    'date': day,
                    'attempts': day_data['attempts'],
                    'correct': day_data['correct'],
                    'accuracy': accuracy
                })
            
            # 全体統計
            total_attempts = sum(day['attempts'] for day in daily_stats)
            total_correct = sum(day['correct'] for day in daily_stats)
            overall_accuracy = (total_correct / total_attempts) * 100 if total_attempts > 0 else 0.0
            
            app_logger.info(f"日別統計計算完了: {len(daily_stats)}日間")
            return {
                'daily_data': daily_stats,
                'total_attempts': total_attempts,
                'total_correct': total_correct,
                'overall_accuracy': overall_accuracy
            }
            
        except Exception as e:
            app_logger.error(f"日別統計計算中にエラーが発生しました: {e}")
            return {
                'daily_data': [],
                'total_attempts': 0,
                'total_correct': 0,
                'overall_accuracy': 0.0
            }
    
    def calculate_mistake_analysis(self) -> Dict[str, Any]:
        """間違い分析を計算"""
        try:
            attempts = self.attempt_storage.load_attempts()
            
            if not attempts:
                return {
                    'mistake_distribution': {},
                    'common_mistakes': [],
                    'improvement_areas': []
                }
            
            # 間違いの種類の分布
            mistake_distribution = defaultdict(int)
            mistake_problems = defaultdict(list)
            
            for attempt in attempts:
                if not attempt.is_correct:
                    mistake_type = attempt.mistake_type
                    mistake_distribution[mistake_type] += 1
                    mistake_problems[mistake_type].append(attempt.problem_id)
            
            # よくある間違いの種類
            common_mistakes = sorted(
                mistake_distribution.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # 改善が必要な領域
            improvement_areas = []
            for mistake_type, count in common_mistakes:
                if count >= 3:  # 3回以上間違えた場合
                    unique_problems = len(set(mistake_problems[mistake_type]))
                    improvement_areas.append({
                        'mistake_type': mistake_type,
                        'count': count,
                        'unique_problems': unique_problems
                    })
            
            app_logger.info(f"間違い分析計算完了: {len(mistake_distribution)}種類")
            return {
                'mistake_distribution': dict(mistake_distribution),
                'common_mistakes': common_mistakes,
                'improvement_areas': improvement_areas
            }
            
        except Exception as e:
            app_logger.error(f"間違い分析計算中にエラーが発生しました: {e}")
            return {
                'mistake_distribution': {},
                'common_mistakes': [],
                'improvement_areas': []
            }
    
    def calculate_learning_progress(self, days: int = 30) -> Dict[str, Any]:
        """学習進捗を計算"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            attempts = self.attempt_storage.load_attempts()
            
            # 期間内の試行をフィルタリング
            period_attempts = [
                a for a in attempts 
                if start_date <= a.timestamp.date() <= end_date
            ]
            
            if not period_attempts:
                return {
                    'period_days': days,
                    'total_attempts': 0,
                    'total_correct': 0,
                    'accuracy': 0.0,
                    'learning_curve': [],
                    'consistency_score': 0.0
                }
            
            # 日別の学習データ
            daily_learning = defaultdict(lambda: {'attempts': 0, 'correct': 0})
            
            for attempt in period_attempts:
                day = attempt.timestamp.date()
                daily_learning[day]['attempts'] += 1
                if attempt.is_correct:
                    daily_learning[day]['correct'] += 1
            
            # 学習曲線の計算
            learning_curve = []
            cumulative_attempts = 0
            cumulative_correct = 0
            
            for day in sorted(daily_learning.keys()):
                day_data = daily_learning[day]
                cumulative_attempts += day_data['attempts']
                cumulative_correct += day_data['correct']
                
                accuracy = (cumulative_correct / cumulative_attempts) * 100 if cumulative_attempts > 0 else 0
                
                learning_curve.append({
                    'date': day,
                    'daily_attempts': day_data['attempts'],
                    'daily_correct': day_data['correct'],
                    'cumulative_attempts': cumulative_attempts,
                    'cumulative_correct': cumulative_correct,
                    'cumulative_accuracy': accuracy
                })
            
            # 一貫性スコア（学習日数 / 期間日数）
            learning_days = len(daily_learning)
            consistency_score = (learning_days / days) * 100
            
            # 全体統計
            total_attempts = sum(day['attempts'] for day in daily_learning.values())
            total_correct = sum(day['correct'] for day in daily_learning.values())
            accuracy = (total_correct / total_attempts) * 100 if total_attempts > 0 else 0.0
            
            app_logger.info(f"学習進捗計算完了: {days}日間")
            return {
                'period_days': days,
                'total_attempts': total_attempts,
                'total_correct': total_correct,
                'accuracy': accuracy,
                'learning_curve': learning_curve,
                'consistency_score': consistency_score
            }
            
        except Exception as e:
            app_logger.error(f"学習進捗計算中にエラーが発生しました: {e}")
            return {
                'period_days': days,
                'total_attempts': 0,
                'total_correct': 0,
                'accuracy': 0.0,
                'learning_curve': [],
                'consistency_score': 0.0
            }


class VisualizationEngine:
    """可視化エンジン"""
    
    def __init__(self):
        self.calculator = StatisticsCalculator()
    
    def create_accuracy_chart(self, problem_stats: Dict[str, Any]) -> go.Figure:
        """正答率チャートを作成"""
        try:
            if not problem_stats:
                return go.Figure()
            
            # データの準備
            problems = []
            accuracies = []
            colors = []
            
            for stats in problem_stats.values():
                problem = stats['problem']
                accuracy = stats['accuracy']
                
                problems.append(f"{problem.answer_kanji}\n({problem.reading})")
                accuracies.append(accuracy)
                
                # 色分け（正答率に応じて）
                if accuracy >= 80:
                    colors.append('green')
                elif accuracy >= 60:
                    colors.append('orange')
                else:
                    colors.append('red')
            
            # チャートの作成
            fig = go.Figure(data=[
                go.Bar(
                    x=problems,
                    y=accuracies,
                    marker_color=colors,
                    text=[f"{acc:.1f}%" for acc in accuracies],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title="問題別正答率",
                xaxis_title="問題",
                yaxis_title="正答率 (%)",
                yaxis=dict(range=[0, 100]),
                height=400
            )
            
            return fig
            
        except Exception as e:
            app_logger.error(f"正答率チャート作成中にエラーが発生しました: {e}")
            return go.Figure()
    
    def create_daily_progress_chart(self, daily_stats: List[Dict[str, Any]]) -> go.Figure:
        """日別進捗チャートを作成"""
        try:
            if not daily_stats:
                return go.Figure()
            
            # データの準備
            dates = [d['date'] for d in daily_stats]
            attempts = [d['attempts'] for d in daily_stats]
            accuracies = [d['accuracy'] for d in daily_stats]
            
            # サブプロットの作成
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('日別試行回数', '日別正答率'),
                vertical_spacing=0.1
            )
            
            # 試行回数チャート
            fig.add_trace(
                go.Bar(x=dates, y=attempts, name='試行回数', marker_color='blue'),
                row=1, col=1
            )
            
            # 正答率チャート
            fig.add_trace(
                go.Scatter(x=dates, y=accuracies, name='正答率', mode='lines+markers', line=dict(color='red')),
                row=2, col=1
            )
            
            fig.update_layout(
                title="学習進捗",
                height=600,
                showlegend=True
            )
            
            fig.update_xaxes(title_text="日付", row=2, col=1)
            fig.update_yaxes(title_text="試行回数", row=1, col=1)
            fig.update_yaxes(title_text="正答率 (%)", row=2, col=1)
            
            return fig
            
        except Exception as e:
            app_logger.error(f"日別進捗チャート作成中にエラーが発生しました: {e}")
            return go.Figure()
    
    def create_mistake_distribution_chart(self, mistake_distribution: Dict[str, int]) -> go.Figure:
        """間違い分布チャートを作成"""
        try:
            if not mistake_distribution:
                return go.Figure()
            
            # データの準備
            mistake_types = list(mistake_distribution.keys())
            counts = list(mistake_distribution.values())
            
            # パイチャートの作成
            fig = go.Figure(data=[
                go.Pie(
                    labels=mistake_types,
                    values=counts,
                    hole=0.3
                )
            ])
            
            fig.update_layout(
                title="間違いの種類分布",
                height=400
            )
            
            return fig
            
        except Exception as e:
            app_logger.error(f"間違い分布チャート作成中にエラーが発生しました: {e}")
            return go.Figure()
    
    def create_learning_curve_chart(self, learning_curve: List[Dict[str, Any]]) -> go.Figure:
        """学習曲線チャートを作成"""
        try:
            if not learning_curve:
                return go.Figure()
            
            # データの準備
            dates = [d['date'] for d in learning_curve]
            cumulative_accuracy = [d['cumulative_accuracy'] for d in learning_curve]
            daily_attempts = [d['daily_attempts'] for d in learning_curve]
            
            # サブプロットの作成
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('累積正答率の推移', '日別試行回数'),
                vertical_spacing=0.1
            )
            
            # 累積正答率チャート
            fig.add_trace(
                go.Scatter(
                    x=dates, 
                    y=cumulative_accuracy, 
                    name='累積正答率', 
                    mode='lines+markers',
                    line=dict(color='blue', width=3)
                ),
                row=1, col=1
            )
            
            # 日別試行回数チャート
            fig.add_trace(
                go.Bar(
                    x=dates, 
                    y=daily_attempts, 
                    name='日別試行回数',
                    marker_color='green'
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title="学習曲線",
                height=600,
                showlegend=True
            )
            
            fig.update_xaxes(title_text="日付", row=2, col=1)
            fig.update_yaxes(title_text="正答率 (%)", row=1, col=1)
            fig.update_yaxes(title_text="試行回数", row=2, col=1)
            
            return fig
            
        except Exception as e:
            app_logger.error(f"学習曲線チャート作成中にエラーが発生しました: {e}")
            return go.Figure()


class StatisticsManager:
    """統計機能の統合管理"""
    
    def __init__(self):
        self.calculator = StatisticsCalculator()
        self.visualizer = VisualizationEngine()
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """包括的な統計情報を取得"""
        try:
            # 問題データの取得
            problems = self.calculator.problem_storage.load_problems()
            
            # 各種統計の計算
            problem_stats = self.calculator.calculate_problem_statistics(problems)
            daily_stats = self.calculator.calculate_daily_statistics()
            mistake_analysis = self.calculator.calculate_mistake_analysis()
            learning_progress = self.calculator.calculate_learning_progress()
            
            # 全体統計
            total_problems = len(problems)
            total_attempts = daily_stats['total_attempts']
            overall_accuracy = daily_stats['overall_accuracy']
            
            app_logger.info(f"包括的統計計算完了: 問題数={total_problems}, 試行数={total_attempts}")
            
            return {
                'overview': {
                    'total_problems': total_problems,
                    'total_attempts': total_attempts,
                    'overall_accuracy': overall_accuracy
                },
                'problem_statistics': problem_stats,
                'daily_statistics': daily_stats,
                'mistake_analysis': mistake_analysis,
                'learning_progress': learning_progress
            }
            
        except Exception as e:
            app_logger.error(f"包括的統計計算中にエラーが発生しました: {e}")
            return {
                'overview': {
                    'total_problems': 0,
                    'total_attempts': 0,
                    'overall_accuracy': 0.0
                },
                'problem_statistics': {},
                'daily_statistics': {'daily_data': []},
                'mistake_analysis': {'mistake_distribution': {}},
                'learning_progress': {'learning_curve': []}
            }
    
    def get_visualization_data(self) -> Dict[str, go.Figure]:
        """可視化データを取得"""
        try:
            # 統計データの取得
            stats = self.get_comprehensive_statistics()
            
            # チャートの作成
            charts = {}
            
            if stats['problem_statistics']:
                charts['accuracy_chart'] = self.visualizer.create_accuracy_chart(stats['problem_statistics'])
            
            if stats['daily_statistics']['daily_data']:
                charts['daily_progress_chart'] = self.visualizer.create_daily_progress_chart(stats['daily_statistics']['daily_data'])
            
            if stats['mistake_analysis']['mistake_distribution']:
                charts['mistake_distribution_chart'] = self.visualizer.create_mistake_distribution_chart(stats['mistake_analysis']['mistake_distribution'])
            
            if stats['learning_progress']['learning_curve']:
                charts['learning_curve_chart'] = self.visualizer.create_learning_curve_chart(stats['learning_progress']['learning_curve'])
            
            app_logger.info(f"可視化データ作成完了: {len(charts)}種類のチャート")
            return charts
            
        except Exception as e:
            app_logger.error(f"可視化データ作成中にエラーが発生しました: {e}")
            return {}
