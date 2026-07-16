# yt2mp3

Petit outil en ligne de commande pour télécharger l'audio d'une vidéo YouTube en MP3, avec estimation du BPM et de la clé/gamme — pratique pour choper des prods/instrus gratuites et les intégrer dans des maquettes.

## Prérequis

- Python 3.9+
- [ffmpeg](https://ffmpeg.org/) installé et disponible dans le `PATH` (`brew install ffmpeg` sur macOS)

## Installation

```bash
cd yt2mp3
python3 -m pip install -r requirements.txt
```

> Recommandé : installer dans un environnement virtuel dédié pour éviter tout conflit de versions avec d'autres projets Python sur ta machine :
> ```bash
> python3 -m venv .venv
> source .venv/bin/activate
> pip install -r requirements.txt
> ```

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

Un disque externe fonctionne aussi tant qu'il est monté, ex. `-o "/Volumes/NomDuDisque/Musique"`.

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

Le dossier par défaut est stocké dans `~/.config/yt2mp3/config.json` (créé automatiquement, `~/Music/yt2mp3` au premier lancement si jamais configuré).

## Analyse BPM / clé

Après chaque téléchargement, l'outil affiche dans le terminal une estimation du BPM et de la clé/gamme du morceau (détection de tempo + analyse chromatique avec l'algorithme de Krumhansl-Schmuckler via `librosa`). Aucune métadonnée n'est écrite dans le fichier.

Le BPM est généralement fiable. La clé est une **approximation statistique** — assez fiable sur des morceaux avec une harmonie/mélodie claire, moins fiable sur des prods très percussives sans partie mélodique nette. À vérifier à l'oreille.

## Raccourcir la commande

Pour éviter de taper `python3 yt2mp3.py` à chaque fois, ajoute un alias dans `~/.zshrc` :
```bash
alias yt2mp3="python3 /chemin/vers/yt2mp3/yt2mp3.py"
```
puis `source ~/.zshrc`.

## Configuration technique

Le script cible les clients `android`/`ios` de YouTube via `yt-dlp` pour contourner le forçage du streaming SABR sur le client web classique. Si l'extraction venait à casser suite à un changement côté YouTube, penser à mettre à jour `yt-dlp` :
```bash
python3 -m pip install --upgrade yt-dlp
```
