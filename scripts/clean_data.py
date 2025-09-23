import csv
from pathlib import Path
import shutil


DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
PROBLEMS = DATA_DIR / 'problems.csv'
ATTEMPTS = DATA_DIR / 'attempts.csv'


def backup(path: Path) -> Path:
    dst = path.with_suffix(path.suffix + '.backup')
    shutil.copy2(path, dst)
    return dst


def load_csv_dicts(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_csv(path: Path, headers: list[str], rows: list[dict]) -> None:
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def clean_problems() -> tuple[int, int]:
    rows = load_csv_dicts(PROBLEMS)
    seen_ids: set[str] = set()
    dedup_rows: list[dict] = []
    for row in rows:
        pid = row.get('id', '')
        if not pid or pid in seen_ids:
            continue
        seen_ids.add(pid)
        if not row.get('incorrect_count'):
            row['incorrect_count'] = '0'
        dedup_rows.append(row)
    headers = ['id', 'sentence', 'answer_kanji', 'reading', 'created_at', 'incorrect_count']
    write_csv(PROBLEMS, headers, dedup_rows)
    return len(rows), len(dedup_rows)


def clean_attempts(valid_problem_ids: set[str]) -> tuple[int, int]:
    rows = load_csv_dicts(ATTEMPTS)
    seen_attempt_ids: set[str] = set()
    cleaned: list[dict] = []
    for row in rows:
        aid = row.get('id', '')
        pid = row.get('problem_id', '')
        if not aid or aid in seen_attempt_ids:
            continue
        if pid not in valid_problem_ids:
            continue
        seen_attempt_ids.add(aid)
        cleaned.append(row)
    headers = ['id', 'problem_id', 'attempted_at', 'is_correct']
    write_csv(ATTEMPTS, headers, cleaned)
    return len(rows), len(cleaned)


if __name__ == '__main__':
    if PROBLEMS.exists():
        backup(PROBLEMS)
    if ATTEMPTS.exists():
        backup(ATTEMPTS)

    before_p, after_p = clean_problems()
    probs = load_csv_dicts(PROBLEMS)
    valid_ids = {r.get('id', '') for r in probs if r.get('id')}
    before_a, after_a = clean_attempts(valid_ids)

    print(f'problems: {before_p} -> {after_p}')
    print(f'attempts: {before_a} -> {after_a}')


