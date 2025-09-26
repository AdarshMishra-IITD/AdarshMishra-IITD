# 🚀 How to Run This Project

Follow these steps to set up and run the Play Store Review Django project on your machine.

## 1. Clone the Repository
```sh
git clone <repo-url>
cd AdarshMishra-IITD
```

## 2. Set Up Python Environment
- Make sure you have Python 3.8+ installed.
- (Recommended) Create a virtual environment:
```sh
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## 3. Install Dependencies
```sh
pip install -r requirements.txt
```

## 4. Configure Environment Variables
- Copy `.env` and set your `DJANGO_SECRET_KEY` and other variables as needed.

## 5. Prepare the Database
```sh
python manage.py migrate
```

## 6. Clean and Import Data
- Place your raw CSVs in `playstore/migrations/csv_data/` (if not already there).
- Run the import command:
```sh
python manage.py import_data
```

## 7. Run the Development Server
```sh
python manage.py runserver
```
- Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## 8. Log In or Register
- Use the web UI to register or log in.

---

## 🛠️ Useful Tips
- To add more data, update the CSVs and rerun the import command.
- For admin access, create a superuser:
```sh
python manage.py createsuperuser
```
- Static files are in `static/` (if used).
- Templates are in `templates/`.

## 📚 Need Help?
- Check the `docs/` folder for more info.
- Ask for a code walkthrough or troubleshooting help anytime!
