# LibDemand AI — Library Book Demand Predictor

Library-la endha books-ku evlo demand varum-nu predict panna help panra project.

## Project-la enna irukku?

- `index.html`, `style.css`, `app.js` — browser-la open aagura interactive web page. Idha GitHub Pages-la publish pannalaam.
- `app.py`, `model.py`, `data_processor.py`, `data_generator.py` — Python + Streamlit dashboard, machine-learning prediction, dataset upload/processing.
- `library_books_dataset.csv` — sample dataset.

## Browser web page-a run pannradhu

Project folder-la terminal open panni:

```bash
python -m http.server 8080
```

Browser-la `http://localhost:8080` open pannunga. GitHub Pages publish aana apram indha static page-ku GitHub Pages URL kidaikkum.

## Streamlit dashboard-a run pannradhu

Python 3 install pannitu project folder-la:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Browser-la `http://localhost:8501` open pannunga. Indha Python dashboard GitHub Pages-la run aagadhu; public-a use panna Streamlit Community Cloud madhiri Python hosting thevai.

## GitHub Pages publish

1. Indha project files-ai GitHub repository-oda root-la upload pannunga.
2. GitHub-la repository **Settings → Pages** open pannunga.
3. **Deploy from a branch** select panni, `main` branch-um `/(root)` folder-um choose pannunga.
4. Save pannina apram Pages URL Settings → Pages-la theriyum. GitHub Pages `index.html`-a serve pannum; Python dashboard-ai serve pannaadhu.

## Streamlit Community Cloud publish

1. Repository-ai GitHub-la push pannunga.
2. Streamlit Community Cloud-la GitHub repository connect pannunga.
3. Main file-a `app.py` select panni deploy pannunga.
4. Kidaikkira `*.streamlit.app` URL-la dashboard-ai share pannalaam.

## Mukkiya files

- `index.html` — static web page structure.
- `style.css` — page design.
- `app.js` — browser interactions, charts, CSV download.
- `app.py` — Streamlit dashboard.
- `model.py` — prediction model.
- `data_processor.py` — CSV/Excel data validation and processing.
- `data_generator.py` — sample library data create pannum.
- `requirements.txt` — Python packages.

## Data privacy

GitHub-la publish panna munnaadi personal/library-private data-ai sample dataset-la include pannala-nu check pannunga. Real patron names, contact details, borrowing histories madhiri private data-ai public repository-la upload pannaadheenga.
