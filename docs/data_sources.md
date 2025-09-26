# 📊 Data Sources & Schema Mapping

This project uses (publicly circulated) Google Play Store datasets. Ensure you respect original licensing / terms of use for any redistribution.

## 1. Source Files
| File | Purpose |
|------|---------|
| `googleplaystore.csv` | Core app metadata (name, category, installs, etc.) |
| `googleplaystore_user_reviews.csv` | User review text + raw sentiment annotations |

These live under `playstore/migrations/csv_data/` so they can be bundled for quick local bootstrap.

## 2. Cleaning Steps (Summary)
Performed by `scripts/clean_data.py`:
- Strip whitespace, normalize casing where appropriate.
- Coerce numeric-ish fields (ratings, polarity, subjectivity) to floats.
- Handle missing values (drop or set to None depending on context).
- Remove obvious duplicates (based on `App` name + other fields) if encountered.
- Export cleaned versions: `*_clean.csv`.

## 3. Field Mapping (googleplaystore.csv → App model)
| CSV Column | App Field | Notes |
|------------|-----------|-------|
| `App` | `name` | Primary display name |
| `Category` | `category` | Text category |
| `Rating` | `rating` | Nullable float |
| `Reviews` | `reviews_count` | Stored as char (could normalize to int future) |
| `Size` | `size` | Raw string (e.g., '19M') |
| `Installs` | `installs` | Raw string (commas & plus signs) |
| `Type` | `type` | 'Free' / 'Paid' |
| `Price` | `price` | String (consider decimal) |
| `Content Rating` | `content_rating` | Audience classification |
| `Genres` | `genres` | Possibly multiple values |
| `Last Updated` | `last_updated` | String; candidate for date parsing |
| `Current Ver` | `current_ver` | Version string |
| `Android Ver` | `android_ver` | Min Android version |

## 4. Field Mapping (googleplaystore_user_reviews.csv → Review model)
| CSV Column | Review Field | Notes |
|------------|--------------|-------|
| `App` | FK via name lookup | Must match existing `App.name` |
| `Translated_Review` | `text` | Only non-null rows imported |
| `Sentiment` | `sentiment` | e.g., Positive / Negative / Neutral |
| `Sentiment_Polarity` | `sentiment_polarity` | Float or None |
| `Sentiment_Subjectivity` | `sentiment_subjectivity` | Float or None |

## 5. Idempotent Import Logic
If any `App` rows exist the import command aborts early to avoid duplication. To force re-import:
1. Drop / flush database.
2. Re-run `python manage.py import_data`.

## 6. Data Quality Considerations
| Issue | Mitigation |
|-------|------------|
| Duplicate app names | `get_or_create` ensures first insert retained |
| Missing sentiment values | Stored as `None`; excluded in aggregates if needed |
| Non-normalized numeric fields | Kept as strings initially to avoid lossy assumptions |

## 7. Potential Improvements
- Normalize `installs` & `price` into numeric fields.
- Parse `last_updated` into `DateField`.
- Add indexing on frequently filtered columns (e.g., `category`).
- Maintain an ingestion log table for provenance.

---
Update this file when adding new data sources or altering schema transformations.
