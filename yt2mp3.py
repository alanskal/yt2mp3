#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import librosa
import numpy as np
import yt_dlp

CONFIG_DIR = Path.home() / ".config" / "yt2mp3"
CONFIG_FILE = CONFIG_DIR / "config.json"
HISTORY_FILE = CONFIG_DIR / "history.json"
FALLBACK_DOWNLOAD_DIR = Path.home() / "Music" / "yt2mp3"

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Profils de Krumhansl-Schmuckler (force tonale perçue de chaque degré de la gamme)
MAJOR_PROFILE = np.array(
    [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
)
MINOR_PROFILE = np.array(
    [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
)


def load_config() -> dict:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def save_config(config: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def get_default_dir() -> Path:
    config = load_config()
    return Path(config.get("download_dir", str(FALLBACK_DOWNLOAD_DIR))).expanduser()


def set_default_dir(path: Path) -> None:
    config = load_config()
    config["download_dir"] = str(path)
    save_config(config)


def load_history() -> list[dict]:
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return []


def add_history_entry(filename: str, bpm: str, key: str) -> None:
    history = load_history()
    history.append(
        {
            "file": filename,
            "bpm": bpm,
            "key": key,
            "date": datetime.now().isoformat(timespec="seconds"),
        }
    )
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def show_history(show_all: bool) -> None:
    history = load_history()
    if not history:
        print("Aucun téléchargement enregistré pour le moment.")
        return

    entries = history if show_all else history[-10:]
    for entry in reversed(entries):
        print(f"{entry['date']}  {entry['file']}  |  clé : {entry['key']}  |  BPM : {entry['bpm']}")


def estimate_key(y: np.ndarray, sr: int) -> str:
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = chroma.mean(axis=1)

    best_score = -np.inf
    best_key = "inconnue"
    for i in range(12):
        major_score = np.corrcoef(chroma_mean, np.roll(MAJOR_PROFILE, i))[0, 1]
        minor_score = np.corrcoef(chroma_mean, np.roll(MINOR_PROFILE, i))[0, 1]
        if major_score > best_score:
            best_score = major_score
            best_key = f"{NOTE_NAMES[i]} Major"
        if minor_score > best_score:
            best_score = minor_score
            best_key = f"{NOTE_NAMES[i]} Minor"
    return best_key


def analyze_audio(path: Path) -> tuple[float, str]:
    y, sr = librosa.load(str(path), sr=None, mono=True)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    bpm = float(np.atleast_1d(tempo)[0])
    key = estimate_key(y, sr)
    return bpm, key


def download_mp3(url: str, output_dir: Path) -> Path | None:
    output_dir.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "noplaylist": True,
        "extractor_args": {"youtube": {"player_client": ["android", "ios"]}},
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        raw_filename = Path(ydl.prepare_filename(info))

    return raw_filename.with_suffix(".mp3")


def download_one(url: str, output_dir: Path) -> None:
    print(f"Téléchargement vers : {output_dir}")
    try:
        mp3_path = download_mp3(url, output_dir)
        print("Terminé.")
    except yt_dlp.utils.DownloadError as e:
        print(f"Erreur de téléchargement : {e}", file=sys.stderr)
        return

    if mp3_path is None:
        return

    print("Analyse audio (BPM / clé)...")
    try:
        bpm, key = analyze_audio(mp3_path)
        bpm_str, key_str = str(round(bpm)), key
        print(f"BPM estimé : {bpm_str}")
        print(f"Clé/gamme estimée : {key_str} (approximation, à vérifier à l'oreille)")
    except Exception as e:
        bpm_str, key_str = "?", "?"
        print(f"Analyse impossible : {e}", file=sys.stderr)

    add_history_entry(mp3_path.name, bpm_str, key_str)


def run_interactive(output_dir: Path) -> None:
    print(f"Mode interactif — dossier de téléchargement : {output_dir}")
    print("Colle un lien YouTube puis Entrée (ligne vide ou 'quit' pour sortir).")
    while True:
        try:
            url = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not url or url.lower() in ("quit", "exit", "q"):
            break
        download_one(url, output_dir)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Télécharge l'audio d'une vidéo YouTube en MP3."
    )
    parser.add_argument("url", nargs="?", help="Lien de la vidéo YouTube")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Dossier de téléchargement pour cette fois seulement (ne change pas le défaut)",
    )
    parser.add_argument(
        "--set-default",
        type=Path,
        metavar="PATH",
        help="Définit le dossier de téléchargement par défaut de façon permanente",
    )
    parser.add_argument(
        "--show-default",
        action="store_true",
        help="Affiche le dossier de téléchargement par défaut actuel",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Liste les derniers téléchargements (nom, clé, BPM). 10 par défaut, voir --all",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Avec --list, affiche tout l'historique au lieu des 10 derniers",
    )
    args = parser.parse_args()

    if args.set_default:
        resolved = args.set_default.expanduser().resolve()
        set_default_dir(resolved)
        print(f"Dossier par défaut mis à jour : {resolved}")
        return

    if args.show_default:
        print(f"Dossier par défaut actuel : {get_default_dir()}")
        return

    if args.list:
        show_history(args.all)
        return

    output_dir = args.output.expanduser().resolve() if args.output else get_default_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.url:
        download_one(args.url, output_dir)
    else:
        run_interactive(output_dir)


if __name__ == "__main__":
    main()
