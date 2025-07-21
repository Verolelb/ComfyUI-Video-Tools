import torch
import numpy as np
from PIL import Image
import os
import shutil
import ffmpeg
import folder_paths # ComfyUI's library for path management

class FPSConverter:
    @classmethod
    def INPUT_TYPES(s):
        """
        Définit les entrées que le node acceptera dans l'interface ComfyUI.
        """
        return {
            "required": {
                "images": ("IMAGE",),
                "original_fps": ("INT", {"default": 8, "min": 1, "max": 120, "step": 1}),
                "target_fps": ("INT", {"default": 24, "min": 1, "max": 120, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "convert_fps"
    CATEGORY = "Video/Interpolation" # Où trouver le node dans le menu

    def convert_fps(self, images, original_fps, target_fps):
        """
        La fonction principale qui exécute la logique du node.
        """
        # Si les FPS sont identiques, pas besoin de traiter, on retourne les images originales.
        if original_fps == target_fps:
            return (images,)

        # Obtenir un dossier temporaire géré par ComfyUI
        temp_dir = folder_paths.get_temp_directory()
        input_dir = os.path.join(temp_dir, "fps_converter_input")
        output_dir = os.path.join(temp_dir, "fps_converter_output")

        # Nettoyer les dossiers temporaires s'ils existent d'une exécution précédente
        if os.path.exists(input_dir):
            shutil.rmtree(input_dir)
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(input_dir)
        os.makedirs(output_dir)

        # --- Étape 1: Sauvegarder les images du Tensor vers des fichiers PNG ---
        # Le format des images en entrée est un Tensor PyTorch. FFmpeg a besoin de fichiers.
        for i, img_tensor in enumerate(images):
            # Conversion du format ComfyUI (tensor, 0-1 float) au format PIL (numpy, 0-255 uint8)
            img_np = np.clip(255. * img_tensor.cpu().numpy(), 0, 255).astype(np.uint8)
            img_pil = Image.fromarray(img_np)
            # Sauvegarder avec un nom numéroté (ex: frame_0001.png)
            img_pil.save(os.path.join(input_dir, f"frame_{i:04d}.png"))
        
        print(f"FPS Converter: Saved {len(images)} frames to temporary directory.")

        # --- Étape 2: Utiliser FFmpeg pour interpoler les images ---
        input_pattern = os.path.join(input_dir, "frame_%04d.png")
        output_pattern = os.path.join(output_dir, "frame_%04d.png")

        try:
            print(f"FPS Converter: Running FFmpeg to convert from {original_fps}fps to {target_fps}fps...")
            (
                ffmpeg
                .input(input_pattern, framerate=original_fps)
                .filter('minterpolate', fps=target_fps, mi_mode='mci')
                .output(output_pattern, start_number=0)
                .run(capture_stdout=True, capture_stderr=True)
            )
            print("FPS Converter: FFmpeg processing complete.")

        except ffmpeg.Error as e:
            # En cas d'erreur, afficher les logs de FFmpeg et lever une exception
            print("FFmpeg Error:")
            print(e.stderr.decode())
            raise e

        # --- Étape 3: Recharger les nouvelles images interpolées dans un Tensor ---
        interpolated_images = []
        output_files = sorted(os.listdir(output_dir))
        for filename in output_files:
            if filename.endswith('.png'):
                img_path = os.path.join(output_dir, filename)
                img_pil = Image.open(img_path)
                # Conversion du format PIL au format ComfyUI
                img_np = np.array(img_pil).astype(np.float32) / 255.0
                img_tensor = torch.from_numpy(img_np)[None,]
                interpolated_images.append(img_tensor)
        
        print(f"FPS Converter: Loaded {len(interpolated_images)} new frames.")

        # Concaténer la liste de tensors en un seul batch
        if not interpolated_images:
             raise Exception("FFmpeg n'a produit aucune image. Vérifiez les FPS et les logs.")
        output_tensor = torch.cat(interpolated_images, dim=0)

        # --- Étape 4: Nettoyage ---
        shutil.rmtree(input_dir)
        shutil.rmtree(output_dir)

        # ComfyUI s'attend à ce que la sortie soit un tuple
        return (output_tensor,)

# --- Enregistrement du Node auprès de ComfyUI ---
# C'est le dictionnaire que ComfyUI va lire pour trouver votre node.
NODE_CLASS_MAPPINGS = {
    "FPSConverter": FPSConverter
}

# Un nom plus lisible pour l'interface.
NODE_DISPLAY_NAME_MAPPINGS = {
    "FPSConverter": "FPS Converter (FFmpeg)"
}