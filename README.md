Backend: 
- Ensure POSTGRES_DB url and GITHUB_PERSONAL_ACCESS_TOKEN are available
- cd backend; pip install -r requirements.txt; flask --app main run --debug

Frontend:
- Ensure clerk publishable key is available in env
- cd frontend; npm install; npm run dev