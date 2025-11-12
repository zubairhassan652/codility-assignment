### 1. Clone the repository
```bash
git clone <your-repo-url>
cd codility-assignment
```

### 2. Create and activate virtual environment
```
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Run Project
```
python manage.py runserver 0.0.0.0:8000
```

### 5. Visit
```
http://localhost:8000/api/jobs/

http://localhost:8000/api/jobs/<id>/

http://localhost:8000/api/import-csv/

http://localhost:8000/api/scrape-jobs/