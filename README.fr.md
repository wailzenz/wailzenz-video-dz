# wailzenz-video-dz 🇩🇿

**Montage vidéo en darija algérienne avec Claude Code — gratuit, et tout tourne sur votre ordinateur.**

Filmez-vous face caméra, donnez la vidéo à Claude, et récupérez un reel 9:16 prêt pour Instagram, TikTok et YouTube Shorts :
silences et erreurs coupés, sous-titres arabes mot par mot, motion design, effets sonores et miniature.

[العربية](README.md) · [English](README.en.md)

![Sous-titres en darija avec traduction arabe des mots français/anglais](docs/img/captions-gloss.png)

## Ce que ça fait

| | |
|---|---|
| ✂️ **Découpage soigné** | Ne coupe que les vraies pauses, jamais au milieu d'un mot ; sur une reprise, garde la deuxième prise |
| 🗣️ **Transcription en darija** | Whisper large-v3 sur le GPU du Mac, ou un modèle entraîné sur la darija algérienne (Hadra) — comparez les deux sur votre voix |
| 💬 **Sous-titres arabes mot par mot** | Lettres liées, sens de droite à gauche, le mot prononcé s'allume |
| 🇫🇷🇬🇧 **Mots français et anglais** | Gardés en lettres latines, suivis d'une traduction arabe entre guillemets : «هادي حاجة normal "عادية"» |
| 🪝 **Hook à l'écran** | Une phrase forte dans les deux premières secondes, vérifiée en darija algérienne |
| 🎬 **Motion design** | 100 animations prêtes, texte qui passe derrière votre tête, cartes, compteurs… |
| 🔀 **Écran partagé qui alterne** | L'animation en haut et votre visage en bas, puis l'inverse — la mise en page change sans cesse |
| 🪟 **Bandeaux en surimpression** | Pas toujours 50/50 : un bandeau fin en haut ou en bas, par-dessus votre vidéo plein écran, sur une carte transparente ou directement sur l'image |
| 🙂 **Jamais de sous-titre sur le visage** | Par-dessus la vidéo plein écran, le sous-titre se place toujours sous le menton — le visage est suivi, et en gros plan l'image remonte un peu pour faire de la place |
| 🧠 **Des visuels, pas un 2e sous-titre** | Les panneaux ne répètent jamais les mots du sous-titre : icônes, maquettes (terminal, timeline), tableaux comparatifs |
| 🔊 **Audio** | Nettoyage de la voix, effets sonores libres de droits, volume à −14 LUFS |
| 🎙️ **Plus que des reels** | Podcast → reels, montage sur le rythme, vidéos motion sans tournage, miniatures |

Tout tourne **en local** : votre vidéo ne quitte pas votre machine.

## Prérequis

- **Claude Code** (nécessite un abonnement Claude — le plugin est gratuit, Claude ne l'est pas).
- **Un Mac**, idéalement Apple Silicon (M1 ou plus récent), 8 Go de RAM minimum (16 Go conseillés), 10 Go libres.
- **Google Chrome** (le moteur de sous-titres l'utilise pour le rendu).
- Windows / Linux : fonctionne avec la transcription portable (`--engine whisper`) ; l'expérience complète est prévue pour Mac. Voir [docs/INSTALL.md](docs/INSTALL.md).

## Installation

Dans Claude Code :

```
/plugin marketplace add wailzenz/wailzenz-video-dz
/plugin install wailzenz-video-dz@wailzenz-video-dz
```

Puis, une seule fois, demandez à Claude : **« installe les outils de wailzenz-video-dz »** — ou lancez :

```bash
bash ~/.claude/plugins/marketplaces/wailzenz-video-dz/setup/setup-mac.sh
```

Environ 4 Go à télécharger (ffmpeg, Whisper, PyTorch…) dans `~/.wailzenz-video-dz`. Détails : [docs/INSTALL.md](docs/INSTALL.md).

## Utilisation

Mettez la vidéo dans un dossier et dites à Claude :

> « monte cette vidéo en reel » · «مونتيلي هاد الفيديو ودير منو ريل» · "edit this video into a reel"

## Crédits

Basé sur **[majed-video](https://github.com/majedphotos/video-ad-editor)** de **Majed Alzaabi** (MIT) — le moteur, les animations et la méthode de montage sont son travail ; merci à lui.
Ce plugin ajoute la couche algérienne : transcription en darija, règles de hook algériennes, traduction arabe des termes en lettres latines, et correction de l'ordre des mots français/anglais dans les sous-titres.
Il ajoute aussi un style maison : écran partagé qui alterne haut/bas, bandeaux en surimpression, sous-titres sous le menton, panneaux qui ne répètent pas le sous-titre, découpage soigné. Liste complète : [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

![](docs/img/split-screens.png)

![](docs/img/overlay-band.png)

## Licence

[MIT](LICENSE). Conservez les mentions des auteurs d'origine.
