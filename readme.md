# 🎉 **Joyeux Anniversaire Anatole** 🎉

---

## **Description**

**Joyeux Anniversaire Anatole** est un **mini-jeu interactif** développé en **Python** avec la bibliothèque **Pygame**. Ce jeu célèbre l'anniversaire d'Anatole en proposant une expérience ludique et personnalisée. Le joueur incarne un **Mario volant**, qui doit éviter des obstacles et atteindre un score pour débloquer une **surprise spéciale**.

---

## **Créé par**

Développé par **Alex-code-lab**.  
Ce projet est **libre d'utilisation** pour des occasions personnelles telles que des anniversaires ou des événements festifs.

---

## **Fonctionnalités**

- **Contrôles intuitifs** : utilisez les flèches haut et bas pour diriger Mario.
- **Animation dynamique** : un cycle jour/nuit basé sur le score du joueur.
- **Gestion des obstacles** : des tuyaux, des nuages et des carapaces mouvantes pour une expérience immersive.
- **Message d'anniversaire personnalisé** : déclenchement d’une vidéo surprise lorsque le joueur atteint un certain score.
- **Adaptabilité** : remplacez facilement la vidéo et le son par vos propres fichiers.

---

## **Compatibilité et Remarques Importantes**

- Le code **a été écrit sur un Mac avec une puce M2**, ce qui influence l'architecture et la compilation. **Attention** : des adaptations sont nécessaires pour :
  - **Des versions plus anciennes de macOS**
  - **Une compilation sous Windows**
- **Version Windows** : le code est fonctionnel sur macOS, mais peut nécessiter des ajustements pour Windows. Une version spécifique à Windows pourra être ajoutée ultérieurement.

---

## **Bibliothèques Python Utilisées**

Le projet repose sur les bibliothèques suivantes :
1. **pygame** : gestion des animations et des interactions
2. **moviepy** : lecture de la vidéo personnalisée
3. **logging** : suivi des événements et débogage
4. **pathlib** : manipulation des chemins des fichiers
5. **sys**, **os**, **time**, **random** : bibliothèques Python standards

---

## **Structure des Fichiers**
```python
2024_11_26_anniv_anatole/
├── main.py                   # Fichier principal du jeu
├── main.spec                 # Fichier de configuration PyInstaller (pour compilation)
├── README.md                 # Ce fichier explicatif
├── resources/                # Dossier contenant toutes les ressources nécessaires
│   ├── mario_volant.png      # Sprite du joueur (Mario volant)
│   ├── brique.png            # Image des obstacles
│   ├── nuage.png             # Sprite des nuages
│   ├── plante.png            # Sprite des plantes
│   ├── carapace_rouge.png    # Sprite des carapaces rouges
│   ├── carapace_verte.png    # Sprite des carapaces vertes
│   ├── SuperMario256.ttf     # Police utilisée dans le jeu
│   ├── mission_joyeux_anniversaire.png # Image de l'écran titre
│   ├── Game_over.png         # Image de l'écran "Game Over"
│   ├── mario_theme_song.mp3  # Musique de fond
│   ├── video_anniv.mp4       # Vidéo personnalisée pour l'anniversaire
│   ├── video_anniv.mp3       # Audio de la vidéo (extrait au format MP3)
│   ├── ffmpeg                # Binaire FFMPEG requis pour MoviePy
│   └── app_icon.icns         # Icône de l'application
```

**Personnalisation : Changer la Vidéo**

	•	La vidéo video_anniv.mp4 est au format classique téléphone (vertical). Vous pouvez la remplacer par une autre vidéo de votre choix.
	•	Extraction du son : extraire l’audio de la vidéo et le convertir en fichier .mp3. Vous pouvez utiliser un outil comme :
	•	FFMPEG (ligne de commande) :

ffmpeg -i video_anniv.mp4 video_anniv.mp3


	•	HandBrake (interface utilisateur).

Guide pour l’Installation

1. Installer Python

	•	Téléchargez et installez la dernière version de Python (>= 3.11) depuis : python.org.
	•	Cochez “Add Python to PATH” lors de l’installation.

2. Installer les Dépendances

	•	Ouvrez un terminal (Anaconda Prompt, cmd ou bash) et exécutez :

```bash
pip install pygame moviepy
```


3. Télécharger les Fichiers

	•	Assurez-vous que tous les fichiers mentionnés dans la structure des dossiers sont en place.

4. Configuration de FFMPEG

FFMPEG est essentiel pour MoviePy. Voici comment l’obtenir :
	1.	Téléchargez FFMPEG depuis ffmpeg.org.
	2.	Extrayez l’archive et placez le fichier ffmpeg dans le dossier resources/.
	3.	Vérifiez que le chemin dans le code est correct :

os.environ["IMAGEIO_FFMPEG_EXE"] = resource_path('resources/ffmpeg')

## **Compilation en Exécutable**

Pour macOS (M2/M1)

	1.	Naviguez dans le dossier du projet :
```bash
cd /chemin/vers/2024_11_26_anniv_anatole
```

	2.	Installer PyInstaller :
```bash
pip install pyinstaller
```

	3.	Compiler le fichier en mode “onefile” :
```bash
pyinstaller main.spec
````
ou
```bash
pyinstaller --onefile main.spec
```


	4.	Résultat :
	•	L’exécutable sera généré dans le dossier dist/ sous le nom JoyeuxAnniversaireAnatole.app.

Pour Windows

	1.	Installez FFMPEG et vérifiez qu’il est accessible via le PATH ou placez le fichier dans resources/.
	2.	Ajustez les chemins dans le code si nécessaire.
	3.	Suivez les mêmes étapes que pour macOS, en modifiant main.spec si des erreurs surviennent.

Protocole d’Utilisation

	1.	Lancez le fichier JoyeuxAnniversaireAnatole.app (macOS) ou JoyeuxAnniversaireAnatole.exe (Windows).
	2.	Contrôlez Mario :
	•	Flèche haut : monter
	•	Flèche bas : descendre
	3.	Appuyez sur Entrée pour mettre en pause ou reprendre le jeu.
	4.	Vidéo de Souhaits : Lorsque le score atteint 10, une vidéo de souhaits d’anniversaire se déclenche !

Limitations et Bugs Connus

	1.	Incompatibilités Windows :
	•	Certaines configurations de MoviePy ou de FFMPEG peuvent poser problème sous Windows.
	•	Une version dédiée Windows pourrait être ajoutée ultérieurement.
	2.	Cycle Jour/Nuit :
	•	En cas de forte baisse de FPS, la transition peut être saccadée.

## **Licence**

Ce projet est sous licence libre pour une utilisation non commerciale. Merci de créditer Alex-code-lab si vous partagez ce projet.


## Amusez-vous bien et joyeux anniversaire, Anatole ! 🎂🎈 

