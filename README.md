# Banking Application 

This is a minimalistic backend for a banking application. 

### Setup inside project

```bash
cd Banking-Application/
python3/python/py -m venv venv
source venv/bin/activate  || venv\Scripts\activate
pip install -r requirements.txt
python -m src.init_db
```

## Run project

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```
