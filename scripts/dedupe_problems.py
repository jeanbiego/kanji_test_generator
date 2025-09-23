import csv
from pathlib import Path
import shutil


def dedupe_problems_csv(csv_path: Path) -> tuple[int, int]:
    if not csv_path.exists():
        return (0, 0)

    # Backup
    backup_path = csv_path.with_suffix('.backup.csv')
    shutil.copy2(csv_path, backup_path)

    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    seen_ids: set[str] = set()
    dedup_rows: list[dict] = []
    for row in rows:
        pid = row.get('id', '')
        if pid in seen_ids:
            continue
        seen_ids.add(pid)
        # backfill missing column
        if not row.get('incorrect_count'):
            row['incorrect_count'] = '0'
        dedup_rows.append(row)

    headers = ['id', 'sentence', 'answer_kanji', 'reading', 'created_at', 'incorrect_count']
    with csv_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(dedup_rows)

    return (len(rows), len(dedup_rows))


if __name__ == '__main__':
    data_dir = Path(__file__).resolve().parent.parent / 'data'
    src = data_dir / 'problems.csv'
    before, after = dedupe_problems_csv(src)
    print(f'deduped {before} -> {after}')


