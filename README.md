# Alpha Vantage Fetch Script
Ce projet contient un script Python simple pour récupérer des données intraday depuis l’API Alpha Vantage.

## Prérequis
- Python 3.9+ recommandé
- Une clé API Alpha Vantage (gratuite) : https://www.alphavantage.co/support/#api-key

## Script
- `alpha_vantage_fetch.py`

## Utilisation
### Option 1 : passer la clé API en argument
```powershell
python .\alpha_vantage_fetch.py --api-key {{ALPHA_VANTAGE_API_KEY}} --symbol IBM --interval 5min --format csv --output-file alpha_vantage_intraday.csv
```

## Import dans Power BI
1. Générez un fichier CSV :
```powershell
python .\alpha_vantage_fetch.py --symbol IBM --interval 5min --format csv --output-file alpha_vantage_intraday.csv
```
2. Ouvrez Power BI Desktop.
3. Cliquez sur **Obtenir des données** > **Texte/CSV**.
4. Sélectionnez le fichier `alpha_vantage_intraday.csv`.
5. Cliquez sur **Charger** (ou **Transformer les données** si vous voulez préparer le modèle).

Le CSV contient les colonnes : `symbol`, `interval`, `timestamp`, `open`, `high`, `low`, `close`, `volume`.

### Option 2 : utiliser une variable d’environnement
```powershell
$env:ALPHA_VANTAGE_API_KEY="{{ALPHA_VANTAGE_API_KEY}}"
python .\alpha_vantage_fetch.py --symbol IBM --interval 5min --format csv --output-file alpha_vantage_intraday.csv
```

### Option 3 : utiliser un fichier de clé API (recommandé pour Power BI)
Créez un fichier `alpha_vantage_api_key.txt` dans le dossier du projet avec la clé sur la première ligne :
```text
{{ALPHA_VANTAGE_API_KEY}}
```
Puis lancez :
```powershell
python .\alpha_vantage_fetch.py --symbol IBM --interval 5min --format csv --output-file alpha_vantage_intraday.csv
```

## Options disponibles
- `--api-key` : clé API Alpha Vantage (optionnelle si `ALPHA_VANTAGE_API_KEY` est définie)
- `--api-key-file` : fichier texte contenant la clé API (défaut : `alpha_vantage_api_key.txt`)
- `--symbol` : symbole boursier (défaut : `IBM`)
- `--interval` : intervalle intraday (`1min`, `5min`, `15min`, `30min`, `60min`; défaut : `5min`)
- `--outputsize` : volume de données (`compact` ou `full`; défaut : `compact`)
- `--format` : format du fichier exporté (`csv` ou `json`; défaut : `csv`)
- `--output-file` : chemin du fichier généré (défaut : `alpha_vantage_intraday.csv`)

## Exemple complet
```powershell
python .\alpha_vantage_fetch.py --symbol AAPL --interval 15min --outputsize compact --format csv --output-file data_aapl.csv
```

## Comportement en cas d’erreur
Le script retourne un code de sortie non nul si :
- la clé API est absente
- l’API retourne une erreur (limite de taux, symbole invalide, etc.)
- une erreur réseau survient

## Dépannage Power BI (erreur ADO.NET)
Si Power BI affiche une erreur du type :
`Échec: fournissez --api-key ou définissez ALPHA_VANTAGE_API_KEY`

Utilisez l’option la plus robuste pour Power BI :
1. Créez `alpha_vantage_api_key.txt` avec votre clé API.
2. Générez le CSV avec le script Python.
3. Importez le CSV dans Power BI via **Obtenir des données > Texte/CSV**.
