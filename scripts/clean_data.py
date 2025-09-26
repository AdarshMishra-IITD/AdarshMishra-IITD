import pandas as pd
import numpy as np
import re

def parse_number(val):
    if pd.isnull(val) or str(val).lower() in ['nan', 'none', '']:
        return np.nan
    val = str(val).strip()
    if val.endswith('M'):
        return int(float(val[:-1]) * 1_000_000)
    if val.endswith(('k', 'K')):
        return int(float(val[:-1]) * 1_000)
    try:
        return int(val.replace(',', ''))
    except Exception:
        return np.nan

def clean_googleplaystore(input_path, output_path):
    df = pd.read_csv(input_path)
    df = df.drop_duplicates()
    df = df[df['App'].notnull()]
    df['Reviews'] = df['Reviews'].apply(parse_number)
    df['Size'] = df['Size'].replace('Varies with device', np.nan)
    df['Installs'] = df['Installs'].astype(str).str.replace('+', '', regex=False).str.replace(',', '', regex=False)
    df['Installs'] = df['Installs'].apply(parse_number)
    df['Price'] = df['Price'].astype(str).replace('$', '', regex=True).replace('Everyone', '0')
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip()
    df = df[(df['Rating'].isnull()) | ((df['Rating'] >= 0) & (df['Rating'] <= 5))]
    df.to_csv(output_path, index=False)
    print(f'Cleaned {input_path} -> {output_path}')

def clean_user_reviews(input_path, output_path):
    df = pd.read_csv(input_path)
    df = df.drop_duplicates()
    df = df[df['Translated_Review'].notnull()]
    df = df[df['Translated_Review'].str.lower() != 'nan']
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip()
    df.to_csv(output_path, index=False)
    print(f'Cleaned {input_path} -> {output_path}')

if __name__ == '__main__':
    base = 'apps/migrations/csv_data/'
    clean_googleplaystore(base + 'googleplaystore.csv', base + 'googleplaystore_clean.csv')
    clean_user_reviews(base + 'googleplaystore_user_reviews.csv', base + 'googleplaystore_user_reviews_clean.csv')
