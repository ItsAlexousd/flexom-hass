# Flexom-HASS : Intégration Flexom pour Home Assistant

Ce projet développe une intégration Home Assistant pour les équipements Flexom de Ubiant, permettant de contrôler et surveiller votre installation domotique à travers l'interface Home Assistant.

## État actuel du projet

🟢 **Développé et fonctionnel**:
- Structure de base de l'intégration
- Authentification à l'API Hemisphere et Hemis
- Connexion WebSocket pour les événements en temps réel
- Support des lumières (contrôle On/Off et variation)

🟡 **En cours de développement**:
- Support des volets roulants
- Support du chauffage

## Guide d'installation

### Installation manuelle

1. **Copier les fichiers**:
   - Téléchargez ce dépôt
   - Copiez le dossier `custom_components/flexom` dans votre répertoire de configuration Home Assistant:
     - Généralement `/config/custom_components/flexom` pour une installation sous Docker ou Home Assistant OS
     - Ou `~/.homeassistant/custom_components/flexom` pour une installation manuelle

2. **Redémarrer Home Assistant**:
   - Allez dans Configuration > Système > Redémarrer

3. **Ajouter l'intégration**:
   - Allez dans Configuration > Intégrations
   - Cliquez sur "Ajouter une intégration" (bouton + en bas à droite)
   - Recherchez "Flexom-Hass"
   - Suivez les instructions pour vous connecter à votre compte Flexom

### Installation via HACS (à venir)

Cette intégration sera bientôt disponible via HACS (Home Assistant Community Store). 

## Configuration

Lors de la configuration, vous aurez besoin de:

- Votre adresse e-mail Ubiant
- Votre mot de passe Ubiant

Ces informations servent à s'authentifier auprès des services Hemisphere et Hemis de Ubiant pour accéder à votre installation Flexom.

## Fonctionnalités

### 1. Éclairage (⚙️ opérationnel)
- Découverte automatique des lumières connectées à Flexom
- Contrôle On/Off
- Variation d'intensité (0-100%)
- Mises à jour d'état en temps réel via WebSocket

### 2. Volets roulants (🔨 en développement)
- Découverte des volets connectés à Flexom
- Contrôle ouverture/fermeture
- Positionnement précis
- Mises à jour d'état en temps réel

### 3. Chauffage (🔨 en développement)
- Découverte des thermostats et radiateurs
- Contrôle des points de consigne
- Modes (confort, éco, etc.)
- Mises à jour d'état en temps réel

## Architecture technique

L'intégration communique avec deux API distinctes:

1. **API Hemisphere**: Pour l'authentification et la récupération des informations du bâtiment
   - Endpoint: `https://hemisphere.ubiant.com`

2. **API Hemis**: Pour le contrôle des appareils et la récupération des données
   - Endpoint: `https://{building_id}.eu-west.hemis.io/hemis/rest`

3. **WebSocket Hemis**: Pour les événements en temps réel
   - Endpoint: URL fournie par l'API Hemisphere

## Structure du projet

```
custom_components/flexom/
├── __init__.py           # Point d'entrée principal
├── config_flow.py        # Interface de configuration
├── const.py              # Constantes et identifiants
├── manifest.json         # Manifeste de l'intégration
├── api.py                # Communication avec l'API Hemis (à venir)
├── websocket.py          # Gestion des événements WebSocket
├── hemis.py              # Client pour l'API Hemis
├── hemisphere.py         # Client pour l'authentification
├── translations/         # Traductions pour l'interface
│   ├── en.json           # Anglais
│   └── fr.json           # Français
└── entities/             # Entités Home Assistant
    ├── __init__.py
    ├── light.py          # Contrôle d'éclairage
    ├── cover.py          # Contrôle des volets (à venir)
    └── climate.py        # Contrôle du chauffage (à venir)
```

## Dépannage

### Connexion à l'API

Si vous rencontrez des problèmes de connexion:
1. Vérifiez vos identifiants
2. Assurez-vous que votre instance Home Assistant a accès à Internet
3. Vérifiez les journaux Home Assistant pour des messages d'erreur spécifiques

### Problèmes avec les appareils

Si certains appareils ne s'affichent pas ou ne répondent pas:
1. Vérifiez qu'ils fonctionnent correctement dans l'application Flexom
2. Redémarrez l'intégration dans Home Assistant
3. Consultez les journaux pour des erreurs spécifiques

## Contribution

Ce projet est open source et les contributions sont les bienvenues! Pour contribuer:

1. Forker le dépôt
2. Créer une branche pour votre fonctionnalité
3. Soumettre une pull request

## Roadmap de développement

1. **Phase 1**: ✅ Structure du projet et authentification
   - Mise en place de la structure de base
   - Implémentation de l'authentification
   - Tests de connexion à l'API

2. **Phase 2**: ✅ Support des lumières
   - Découverte des équipements
   - Implémentation du contrôle de base
   - Support du WebSocket pour les états en temps réel

3. **Phase 3**: 🔄 Support des volets roulants
   - Implémentation des entités Cover
   - Contrôle et états des volets

4. **Phase 4**: 🔄 Support du chauffage
   - Implémentation des entités Climate
   - Gestion des programmes et températures

5. **Phase 5**: 🔄 Documentation et optimisation
   - Documentation complète
   - Tests et corrections de bugs
   - Optimisation des performances

## Ressources

- [Documentation de l'API Hemis](docs/hemis/)
- [Documentation Home Assistant pour les développeurs](https://developers.home-assistant.io/)

## Remerciements

- Ubiant pour la solution Flexom
- La communauté Home Assistant pour leurs outils et support

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
