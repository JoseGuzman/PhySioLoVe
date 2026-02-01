#!/usr/bin/env python
"""
Import health data from CSV/TSV file
Usage: uv run python scripts/import_data.py data/health_data.csv
"""
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app, db, HealthEntry

def parse_time(time_str):
    """Convert time string (h:mm:ss) to hours as float"""
    if pd.isna(time_str) or time_str == '--' or time_str == '':
        return None
    try:
        parts = str(time_str).split(':')
        hours = int(parts[0]) + int(parts[1])/60
        return round(hours, 2)
    except:
        return None

def parse_number(value):
    """Parse number with comma as decimal separator"""
    if pd.isna(value) or value == '--' or value == '':
        return None
    try:
        return float(str(value).replace(',', '.'))
    except:
        return None

def parse_date(date_str):
    """Parse date in various formats"""
    if pd.isna(date_str) or date_str == '--' or date_str == '':
        return None
    
    # Try different date formats
    formats = ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y']
    for fmt in formats:
        try:
            return datetime.strptime(str(date_str).strip(), fmt).date()
        except:
            continue
    return None

def import_data(filepath):
    """Import data from CSV/TSV file"""
    print(f"\n📊 Importing data from {filepath}...")
    
    # Detect separator (CSV or TSV)
    if filepath.endswith('.tsv'):
        sep = '\t'
    else:
        sep = ','
    
    # Read file
    df = pd.read_csv(filepath, sep=sep, encoding='utf-8')
    
    # Print column names to help debug
    print(f"\n📋 Found columns: {list(df.columns)}\n")
    
    # Map column names (handle variations)
    column_map = {}
    for col in df.columns:
        col_lower = col.lower().strip()
        if 'date' in col_lower:
            column_map['date'] = col
        elif 'weight' in col_lower and 'kg' in col_lower:
            column_map['weight'] = col
        elif 'body' in col_lower and 'fat' in col_lower:
            column_map['body_fat'] = col
        elif 'calorie' in col_lower:
            column_map['calories'] = col
        elif 'step' in col_lower:
            column_map['steps'] = col
        elif 'sleep total' in col_lower:
            column_map['sleep_total'] = col
        elif 'sleep quality' in col_lower:
            column_map['sleep_quality'] = col
        elif 'observation' in col_lower:
            column_map['observations'] = col
    
    print(f"📌 Mapped columns: {column_map}\n")
    
    if 'date' not in column_map:
        print("❌ Error: Could not find a 'Date' column!")
        print(f"Available columns: {list(df.columns)}")
        sys.exit(1)
    
    added = 0
    skipped = 0
    errors = 0
    
    with app.app_context():
        for idx, row in df.iterrows():
            try:
                date = parse_date(row[column_map['date']])
                if not date:
                    errors += 1
                    continue
                
                # Check if entry exists
                existing = HealthEntry.query.filter_by(date=date).first()
                if existing:
                    skipped += 1
                    continue
                
                # Create new entry
                entry = HealthEntry(
                    date=date,
                    weight=parse_number(row.get(column_map.get('weight'))) if 'weight' in column_map else None,
                    body_fat=parse_number(row.get(column_map.get('body_fat'))) if 'body_fat' in column_map else None,
                    calories=int(parse_number(row.get(column_map.get('calories')))) if 'calories' in column_map and parse_number(row.get(column_map.get('calories'))) else None,
                    steps=int(parse_number(row.get(column_map.get('steps')))) if 'steps' in column_map and parse_number(row.get(column_map.get('steps'))) else None,
                    sleep_total=parse_time(row.get(column_map.get('sleep_total'))) if 'sleep_total' in column_map else None,
                    sleep_quality=row.get(column_map.get('sleep_quality')) if 'sleep_quality' in column_map and pd.notna(row.get(column_map.get('sleep_quality'))) and row.get(column_map.get('sleep_quality')) != '--' else None,
                    observations=row.get(column_map.get('observations')) if 'observations' in column_map and pd.notna(row.get(column_map.get('observations'))) else None
                )
                
                db.session.add(entry)
                added += 1
                
            except Exception as e:
                errors += 1
                print(f"⚠️  Error on row {idx + 1}: {e}")
                continue
        
        db.session.commit()
    
    print(f"✓ Import complete!")
    print(f"  • Added: {added} entries")
    print(f"  • Skipped: {skipped} entries (already exist)")
    print(f"  • Errors: {errors} entries (invalid data)")
    
    total = HealthEntry.query.count()
    print(f"  • Total in database: {total}\n")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: uv run python scripts/import_data.py <path_to_file>")
        print("Example: uv run python scripts/import_data.py data/health_data.csv")
        sys.exit(1)
    
    filepath = sys.argv[1]
    if not Path(filepath).exists():
        print(f"Error: File '{filepath}' not found")
        sys.exit(1)
    
    import_data(filepath)
