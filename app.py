import os
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from gtts import gTTS, lang
import warnings
import soundfile as sf

warnings.filterwarnings('ignore')

# Créez un dossier temporaire
temp_dir = os.path.join(os.getcwd(), "temp")
os.makedirs(temp_dir, exist_ok=True)

# Fonction pour convertir le texte en parole
def text_to_speech(text, language, voice_option="standard"):
    try:
        # Paramètres selon l'option de voix
        slow = (voice_option == "lent")
        
        # Création de l'objet gTTS
        tts = gTTS(text=text, lang=language, slow=slow)
        
        # Sauvegarde temporaire
        output_path = os.path.join(temp_dir, f"output_{voice_option}.mp3")
        tts.save(output_path)
        
        return output_path
    except Exception as e:
        st.error(f"Erreur lors de la génération audio: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None

# Interface principale
def main():
    st.title("VocalIA - Assistant de Synthèse Vocale")
    st.markdown("Transformez vos textes en voix naturelles")
    
    # Entrée du texte
    text = st.text_area(
        "Texte à convertir en audio",
        placeholder="Entrez votre texte ici...",
        height=150
    )
    
    # Sélection de la langue
    lang_options = {
        "Français": "fr",
        "Anglais": "en",
        "Espagnol": "es",
        "Allemand": "de",
        "Italien": "it",
        "Portugais": "pt",
        "Néerlandais": "nl"
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        language_name = st.selectbox(
            "Langue",
            options=list(lang_options.keys()),
            index=0
        )
        language = lang_options[language_name]
    
    with col2:
        voice_option = st.selectbox(
            "Type de voix",
            options=["standard", "lent"],
            index=0,
            help="Options de voix disponibles"
        )
    
    # Bouton pour générer l'audio
    if st.button("Générer l'audio"):
        if not text:
            st.error("Veuillez entrer un texte à convertir.")
        else:
            with st.spinner("Génération de l'audio en cours..."):
                audio_file = text_to_speech(text, language, voice_option)
                
                if audio_file:
                    st.success("Audio généré avec succès!")
                    
                    # Affichage de l'audio
                    st.audio(audio_file)
                    
                    # Bouton de téléchargement
                    with open(audio_file, "rb") as file:
                        btn = st.download_button(
                            label="Télécharger l'audio",
                            data=file,
                            file_name=f"vocalia_{language}_{voice_option}.mp3",
                            mime="audio/mp3"
                        )
    
    # Informations sur les limitations
    st.info("""
    **Note sur les types de voix:** Cette version simplifiée ne permet que les options standard et lente.
    Pour avoir plus d'options (masculin, féminin), il faudrait installer ffmpeg sur votre Mac :
    ```
    brew install ffmpeg
    ```
    """)

if __name__ == "__main__":
    main()