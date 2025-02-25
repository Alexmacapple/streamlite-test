# @title Création et activation d'un environnement virtuel
!pip install virtualenv
!virtualenv venv_tts
!source /content/venv_tts/bin/activate

# @title Installation des dépendances dans l'environnement virtuel
!pip install TTS gradio torch soundfile

# @title Vérification du GPU
import torch
print(f"GPU disponible: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Modèle de GPU: {torch.cuda.get_device_name(0)}")

# @title Script complet TTS dans l'environnement virtuel
%%writefile /content/run_tts.py
from transformers.utils import logging
from TTS.api import TTS
import torch
import gradio as gr
import soundfile as sf
from torch.serialization import add_safe_globals
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
import os

# Configuration de sécurité
add_safe_globals([
    XttsConfig,
    XttsAudioConfig,
    XttsArgs,
    BaseDatasetConfig
])

# Suppression des avertissements
logging.set_verbosity_error()

# Détection automatique du GPU pour Colab
USE_GPU = torch.cuda.is_available()

def generate_speech(text, language, speaker_wav=None):
    try:
        # Initialisation du modèle
        tts = TTS(
            model_name="tts_models/multilingual/multi-dataset/xtts_v2",
            progress_bar=True,
            gpu=USE_GPU  # Utilisation automatique du GPU si disponible
        )
        
        # Génération de l'audio
        if speaker_wav:
            audio = tts.tts(
                text=text,
                language=language,
                speaker_wav=speaker_wav,
                enable_text_splitting=True
            )
        else:
            audio = tts.tts(
                text=text,
                language=language,
                speaker="Ana Florence",  # Voix par défaut
                enable_text_splitting=True
            )
        
        # Sauvegarde de l'audio dans un répertoire temporaire de Colab
        output_path = "/content/output.wav"
        sf.write(output_path, audio, tts.synthesizer.output_sample_rate)
        
        # Libération des ressources
        del tts
        if USE_GPU:
            torch.cuda.empty_cache()
        
        return output_path
        
    except Exception as e:
        print(f"Erreur : {str(e)}")
        return None
    finally:
        # Nettoyage supplémentaire
        if 'tts' in locals():
            del tts
        if USE_GPU:
            torch.cuda.empty_cache()

# Interface Gradio
interface = gr.Interface(
    fn=generate_speech,
    inputs=[
        gr.Textbox(
            label="Texte à convertir en audio",
            placeholder="Entrez votre texte ici...",
            lines=5
        ),
        gr.Dropdown(
            choices=["fr", "en", "es", "de", "it", "pt", "nl", "pl", "ru", "cs", "ar", "zh-cn", "hu", "ko", "ja"],
            label="Langue",
            value="fr"
        ),
        gr.Audio(
            label="Voix de référence (optionnel)",
            type="filepath"
        )
    ],
    outputs=[
        gr.Audio(
            label="Audio généré",
            type="filepath"
        )
    ],
    title="VocalIA - Assistant de Synthèse Vocale",
    description="Transformez vos textes en voix naturelles ou clonez une voix existante"
)

if __name__ == "__main__":
    try:
        interface.launch(debug=True, share=True)
    except KeyboardInterrupt:
        print("\nFermeture de l'application...")
    finally:
        # Nettoyage final
        if os.path.exists("/content/output.wav"):
            try:
                os.remove("/content/output.wav")
            except:
                pass
        if USE_GPU:
            torch.cuda.empty_cache()
        print("\nApplication terminée.")

# @title Exécuter l'application depuis l'environnement virtuel
!source /content/venv_tts/bin/activate && python /content/run_tts.py

# @title Nettoyage de l'environnement (à exécuter à la fin)
def cleanup():
    # Suppression des fichiers temporaires
    if os.path.exists("/content/output.wav"):
        try:
            os.remove("/content/output.wav")
            print("Fichier audio temporaire supprimé.")
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier audio: {e}")
    
    # Libération de la mémoire GPU
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        print("Mémoire GPU libérée.")
    
    print("Nettoyage terminé.")

# Exécuter le nettoyage
import os
import torch
cleanup()