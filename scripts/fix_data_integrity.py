#!/usr/bin/env python3
"""
データ整合性修正スクリプト
problems.csvとattempts.csvのID重複を解消し、incorrect_countを合算する
"""

import csv
import os
import shutil
from datetime import datetime

def create_backup():
    """バックアップファイルを作成"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # problems.csvのバックアップ
    if os.path.exists('data/problems.csv'):
        shutil.copy2('data/problems.csv', f'data/problems_before_fix_{timestamp}.csv')
        print(f"✓ problems.csvのバックアップを作成: data/problems_before_fix_{timestamp}.csv")
    
    # attempts.csvのバックアップ
    if os.path.exists('data/attempts.csv'):
        shutil.copy2('data/attempts.csv', f'data/attempts_before_fix_{timestamp}.csv')
        print(f"✓ attempts.csvのバックアップを作成: data/attempts_before_fix_{timestamp}.csv")

def fix_problems_csv():
    """problems.csvの重複ID解消とincorrect_count合算"""
    print("problems.csvの修正を開始...")
    
    # CSVファイルを読み込み
    problems = []
    with open('data/problems.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            problems.append(row)
    
    print(f"読み込み完了: {len(problems)}件の問題")
    
    # 重複IDを特定し、incorrect_countを合算
    id_to_problem = {}
    duplicates = []
    
    for i, problem in enumerate(problems):
        problem_id = problem['id']
        if problem_id in id_to_problem:
            # 重複発見
            original_index = id_to_problem[problem_id]
            duplicates.append((i, original_index, problem))
            
            # incorrect_countを合算
            original_count = int(problems[original_index]['incorrect_count'])
            duplicate_count = int(problem['incorrect_count'])
            problems[original_index]['incorrect_count'] = str(original_count + duplicate_count)
            
            print(f"重複発見: ID {problem_id}")
            print(f"  元のincorrect_count: {original_count}, 重複: {duplicate_count}, 合算後: {original_count + duplicate_count}")
        else:
            id_to_problem[problem_id] = i
    
    print(f"重複レコード数: {len(duplicates)}件")
    
    # 重複レコードを削除（後ろから削除してインデックスを保持）
    for i, original_index, problem in reversed(duplicates):
        del problems[i]
        print(f"重複レコード削除: 行{i+1} (ID: {problem['id']})")
    
    # 最終空行を削除
    if problems and not problems[-1]['id'].strip():
        del problems[-1]
        print("最終空行を削除")
    
    # 修正後のデータを保存
    with open('data/problems.csv', 'w', encoding='utf-8', newline='') as f:
        if problems:
            fieldnames = problems[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(problems)
    
    print(f"✓ problems.csv修正完了: {len(problems)}件の問題")
    return len(problems)

def fix_attempts_csv():
    """attempts.csvの存在しないproblem_id参照削除"""
    print("attempts.csvの修正を開始...")
    
    # problems.csvから有効なproblem_idを取得
    valid_problem_ids = set()
    with open('data/problems.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            valid_problem_ids.add(row['id'])
    
    print(f"有効なproblem_id数: {len(valid_problem_ids)}")
    
    # attempts.csvを読み込み
    attempts = []
    invalid_attempts = []
    
    with open('data/attempts.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if row['problem_id'] in valid_problem_ids:
                attempts.append(row)
            else:
                invalid_attempts.append((i+1, row))
                print(f"無効なproblem_id参照: 行{i+1}, problem_id: {row['problem_id']}")
    
    print(f"削除対象の試行レコード数: {len(invalid_attempts)}件")
    
    # 最終空行を削除
    if attempts and not attempts[-1]['id'].strip():
        del attempts[-1]
        print("最終空行を削除")
    
    # 修正後のデータを保存
    with open('data/attempts.csv', 'w', encoding='utf-8', newline='') as f:
        if attempts:
            fieldnames = attempts[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(attempts)
    
    print(f"✓ attempts.csv修正完了: {len(attempts)}件の試行")
    return len(attempts)

def verify_results():
    """修正結果の検証"""
    print("修正結果の検証を開始...")
    
    # problems.csvの検証
    problems = []
    problem_ids = set()
    with open('data/problems.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            problems.append(row)
            if row['id'] in problem_ids:
                print(f"❌ 重複ID発見: {row['id']}")
                return False
            problem_ids.add(row['id'])
    
    print(f"✓ problems.csv: {len(problems)}件の問題、重複IDなし")
    
    # attempts.csvの検証
    attempts = []
    invalid_refs = []
    with open('data/attempts.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            attempts.append(row)
            if row['problem_id'] not in problem_ids:
                invalid_refs.append(row['problem_id'])
    
    if invalid_refs:
        print(f"❌ 存在しないproblem_id参照: {invalid_refs}")
        return False
    
    print(f"✓ attempts.csv: {len(attempts)}件の試行、すべて有効なproblem_id参照")
    
    # incorrect_countの合算結果を表示
    print("\nincorrect_count合算結果:")
    for problem in problems:
        if int(problem['incorrect_count']) > 0:
            print(f"  {problem['id']}: {problem['incorrect_count']} (問題: {problem['sentence'][:20]}...)")
    
    print("\n✓ すべての検証が完了しました")
    return True

def main():
    """メイン処理"""
    print("=== データ整合性修正スクリプト ===")
    
    try:
        # ステップ1: バックアップ作成
        print("\n[ステップ1] バックアップ作成")
        create_backup()
        
        # ステップ2: problems.csv修正
        print("\n[ステップ2] problems.csv修正")
        problem_count = fix_problems_csv()
        
        # ステップ3: attempts.csv修正
        print("\n[ステップ3] attempts.csv修正")
        attempt_count = fix_attempts_csv()
        
        # ステップ4: 検証
        print("\n[ステップ4] 検証")
        if verify_results():
            print(f"\n🎉 修正完了!")
            print(f"  問題数: {problem_count}件")
            print(f"  試行数: {attempt_count}件")
        else:
            print("\n❌ 検証に失敗しました")
            return False
            
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
