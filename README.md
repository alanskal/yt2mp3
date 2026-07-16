# yt2mp3

Petit outil en ligne de commande pour télécharger l'audio d'une vidéo YouTube en MP3, avec estimation du BPM et de la clé/gamme 

## Prérequis

- Python 3.9+
- [ffmpeg](https://ffmpeg.org/) installé et disponible dans le `PATH`
  - macOS : `brew install ffmpeg`
  - Windows : `winget install ffmpeg` (ou télécharger sur [ffmpeg.org](https://ffmpeg.org/download.html) et l'ajouter au `PATH`)

> Note Windows : partout où ce README écrit `python3`, utilise `python` à la place (le lanceur officiel Windows s'appelle `python`, pas `python3`).

## Installation

**macOS / Linux :**
```bash
git clone https://github.com/alanskal/yt2mp3.git
cd yt2mp3
python3 -m pip install -r requirements.txt
```

**Windows (PowerShell ou cmd) :**
```powershell
git clone https://github.com/alanskal/yt2mp3.git
cd yt2mp3
python -m pip install -r requirements.txt
```

## Usage

Télécharger un lien directement :
```bash
python3 yt2mp3.py "https://youtube.com/watch?v=..."
```

Mode interactif (colle plusieurs liens à la suite sans relancer la commande) :
```bash
python3 yt2mp3.py
# > colle un lien, Entrée, ça télécharge, ça redemande...
# ligne vide, 'quit' ou Ctrl+C pour sortir
```

Choisir un dossier de destination ponctuel (sans changer le défaut) :
```bash
python3 yt2mp3.py "https://youtube.com/watch?v=..." -o /autre/chemin
```

Un disque externe fonctionne aussi tant qu'il est branché, ex. `-o "/Volumes/NomDuDisque/Musique"` sur macOS, ou `-o "E:\Musique"` sur Windows (remplace `E:` par la lettre de ton disque).

Changer le dossier de téléchargement par défaut de façon permanente :
```bash
python3 yt2mp3.py --set-default ~/Musique/YoutubeMP3
```

Afficher le dossier par défaut actuel :
```bash
python3 yt2mp3.py --show-default
```

Lister les derniers téléchargements (nom du fichier, clé, BPM) — 10 par défaut :
```bash
python3 yt2mp3.py --list
```

Voir tout l'historique :
```bash
python3 yt2mp3.py --list --all
```

Le dossier par défaut est stocké dans `~/.config/yt2mp3/config.json` (soit `C:\Users\<toi>\.config\yt2mp3\config.json` sur Windows), créé automatiquement, `~/Music/yt2mp3` au premier lancement si jamais configuré.

## Analyse BPM / clé

Après chaque téléchargement, l'outil affiche dans le terminal une estimation du BPM et de la clé/gamme du morceau (détection de tempo + analyse chromatique avec l'algorithme de Krumhansl-Schmuckler via `librosa`).

Le BPM est généralement fiable. La clé est une **approximation statistique** on obtient des résultats aussi fiables que **TuneBat**

