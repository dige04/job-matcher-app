# Job Matcher App (demo)

## Quick start (local)
1. Put your PhoBERT model and tokenizer inside `backend/artifacts/model` and `backend/artifacts/tokenizer`.
2. Backend:
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run.sh

markdown
Copy code
3. Frontend:
cd frontend
npm install
npm run dev

markdown
Copy code
4. Visit `http://localhost:3000` and paste resume + job post.

## Notes
- To use your own sentence-embedding model, edit `inference.DEFAULT_EMBED_MODEL`.
- Tune similarity `threshold` in `inference.SkillMatcher.compute_missing_skills`.