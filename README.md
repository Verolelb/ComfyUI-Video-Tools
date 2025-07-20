# ComfyUI-Video-Tools
A custom node for ComfyUI to convert video FPS using FFmpeg interpolation
# ComfyUI Video Tools

Un ensemble de nodes pour la manipulation de vidéo dans ComfyUI. Ce projet est fait par [Verolelb](https://github.com/Verolelb).

## Nodes Inclus

### 🎥 FPS Converter (FFmpeg)
Ce node permet de changer le nombre d'images par seconde (FPS) d'une séquence d'images en utilisant l'interpolation de mouvement de FFmpeg pour un résultat fluide. Idéal pour convertir des animations générées image par image (ex: 8 fps) en une vidéo standard (ex: 24 fps).

## Installation

1.  **Prérequis :** Vous devez avoir [FFmpeg](https://ffmpeg.org/download.html) installé sur votre système et accessible depuis le terminal.
2.  Installez ce node via le [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager).

## Exemple de Workflow

Voici un exemple simple pour convertir une vidéo de 8fps à 24fps.

https://imgur.com/a/GjDMkgt

1.  **Load Video** : Charge la vidéo et la sépare en images.
2.  **FPS Converter (FFmpeg)** : Prend les images et le FPS original, et génère de nouvelles images au FPS cible.
3.  **Video Combine** : Recompile les images interpolées en un nouveau fichier vidéo.

## Dépendances
- [FFmpeg](https://ffmpeg.org/download.html) (doit être installé manuellement)
- `ffmpeg-python` (installé automatiquement par le ComfyUI Manager)
