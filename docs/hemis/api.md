# [](#bienvenue-dans-la-documentation-avancee-d-hemis)Bienvenue dans la documentation avancée d'Hemis

- - -

Suite aux étapes d'authentifications afin de récupérer le **session\_token** ainsi que la **base\_url** de l'Hemis et les étapes d'initiation aux APIs, il est possible d'appronfondir par le biais de cette documentation avancée.

- - -

**Voici quelques notions réunies dans Hemis :**

*   [Agenda](/hemis#agenda), correspond aux planifications effectuées sur l'Hemis.
*   [Ambiance](/hemis#ambiance), correspond à une atmosphère particulière sauvegardée sur l'Hemis.
*   [Apprentissage](/hemis#apprentissage), permet de récupérer des prédictions faitent sur une période donnée suite à l'apprentissage effectué par l'Hemis.
*   [Compte](/hemis#compte), correspond à la gestion de compte tiers, comme par exemple un compte Phillips Hue pour les ampoules.
*   [Connecteur](/hemis#connecteur), correspond aux liens entre objets afin de modéliser les réseaux et cablâges dans le système d'Hemis.
*   [DataProvider](/hemis#data-provider), service permettant de consulter, par des requêtes personnalisables, toutes les données des séries temporelles de l'hemis (capteurs, actionneurs, facteurs, events, données externes, events, ITStates, etc. ).
*   [Facteur](/hemis#facteur), correspond aux facteurs environnementaux. Il est par exemple possible de récupérer tous les facteurs environnementaux actifs d'une zone. Un facteur environnemental peut être la température, la luminosité, la luminosité extérieure, pour les principaux. Une liste exaustive de tous les facteurs existants est disponnible [ici](/custom/factors)
*   [Objet intelligent](/hemis#objet-intelligent), correspond à l'ensemble des manipulations possibles sur les objets intelligents de l'Hemis.
*   [Passerelle](/hemis#passerelle), correspond aux passerelles de l'Hemis.
*   [Scenario](/hemis#scenario), correspond aux alertes et aux objectifs de la consommation de l'Hemis.
*   [System](/hemis#system), correspond à la partie système de l'Hemis. Cette partie permet notamment d'exporter le batch de l'Hemis. Le batch étant la minimisation des données sur un fichier. Il est possible aussi de voir l'état du containeur sur lequel se trouve l'Hemis. De plus, il est possible d'injecter des évènements type, augmenter la luminosité.
*   [Tag](/hemis#tag), correspond à des identifiants placés sur des tags NFC ou QR codes afin de leur donner des actions à effectuer lors de leur analyse.
*   [Tarification](/hemis#tarification) permet d'ajouter des tarifications afin d'avoir des idées de prix sur une période donnée de la consommation sur un facteur environnemental.
*   [Utilisateur](/hemis#utilisateur), permet de récupérer le session\_token de l'Hemis, utilisé pendant la phase d'authentification préalablement faite.
*   [Zone](/hemis#zones), correspond à une pièce ou un ensemble de pièces.

Afin de pouvoir suivre les concepts en parrallèles, il est possible d'importer toute la configuration **Postman**.  
Il faut pour cela avoir fait préalablement la partie authentification dans le tutoriel. ([tutoriel](/tutoriels/authentification))

[![Run in Postman](https://run.pstmn.io/button.svg)](https://app.getpostman.com/run-collection/4bf330e169d074b80b5f)

- - -

# [](#agenda)Agenda

Un agenda correspond aux planifications effectuées sur une zone en fonction d'un facteur environnemental. Il est possible d'ajouter des exceptions entre deux dates voulues de l'agenda de base.

[Documentation Swagger correspondante](https://developers.ubiant.com/swagger/hemis#/agendas)

**Voici les différentes actions à effectuer sur les agendas** :

## [](#ajouter-un-agenda)Ajouter un agenda

**'Post': {hemis\_base\_url}/zones/{zoneId}/agendas/{factorId}**  
Pour effectuer cette requête, le factorId et le zoneId se passent en "path parameter" et le contenu de l'objet agenda est au format json dans le "body" de la requête.

Dans un premier temps, pour ajouter un agenda il faut choisir un facteur environnemental ([liste des facteurs](/custom/factors)) :

*   La température ("factorId" : "TMP")
*   La luminosité ("factorId" : "BRI")
*   L'occultation ("factorId" : "BRIEXT")

```
{
    "factorId": {
        "factor": "{factorId}",
                ...
        }		
        ...
}
```

Puis il faut choisir une zone :

```
{
    "factorId": {
        "factor": "{factorId}",
        "zoneName": "{zoneId}"
    },
        ...
}
```

Ensuite, il faut configurer la valeur voulue du facteur environnemental :

```
{
    "factorId": {
        ...
        }		
        "targetValues": {
        "": {
            "name": "",
            "value": 20,
            "type": "AUTO",
            "minValue": 19.5,
            "maxValue": 20.5,
            "orientation": "AUTO"
        }
        },
        ...
}
```

Enfin il faut configurer les intervalles pour chaque jour.  
L'heure est en minutes à partir du début de la journée. Par exemple pour midi il faut faire 12 (heures) \* 60 (minutes) = 720 minutes

```
{
    "factorId": {
        ...
        }		
        "targetValues": {
                ...
        }
        },
        "days": {
        "THU": {
            "intervals": [
                {
                    "timeStart": 0,
                    "timeEnd": 720,
                    "value": {
                        "name": "",
                        "value": 16.9,
                        "type": "AUTO",
                        "minValue": 16.4,
                        "maxValue": 17.4,
                        "orientation": "AUTO"
                    }
               },
                    ]
            },
            ...
}
```

Voici un exemple complet d'ajout d'un agenda au format json: [Ajouter un agenda](/uploads/addagenda.json "Addagenda")

## [](#ajouter-une-exception-a-un-agenda)Ajouter une exception à un agenda

**'Post': {hemis\_base\_url}/zones/{zoneId}/agendas/{factorId}/overrides**  
Pour effectuer cette requête, le factorId et le zoneId se passent en "path parameter" et le contenu de l'objet de l'exception est au format json dans le "body" de la requête.

Exemple d'une exception sur la température pour le 20 et 21 mars 2019 entre minuit et midi.  
Pour cela il faut:

*   donner une priorité sur l'exception, l'ordre de priorité est croissant, une priorité 1 prendra l'avantage sur une priorité 0. Attention l'action peut-être refusée si il y a une exception déjà existante sur la période voulue avec la même priorité. Voir les [conflits d'exceptions](https://developers.ubiant.com/hemis/#recuperer-les-conflits-dexceptions) pour apprendre à les gérer.
*   nommer l'exception
*   lui donner l'heure d'intervalle en minutes. Exemple: midi = 12 heures \* 60 minutes = 720 minutes
*   lui donner une valeur de température voulue
*   indiquer la température minimum et maximum a ne pas dépasser
*   indiquer la date de début et de fin au format 'dd/MM/yyyy’

Voici le corps du json pour l'exemple donné:

```
{
    "id": null,
    "name": "ExempleException",
    "priority": 0,
    "intervals": [
        {
            "timeStart": 0,
            "timeEnd": 720,
            "value": {
                "name": "",
                "value": 13.2,
                "type": "AUTO",
                "minValue": 12.7,
                "maxValue": 13.7,
                "orientation": "AUTO"
            }
        }
    ],
    "temporalDefinition": {
        "type": "START_END",
        "startDate": "20/03/2019",
        "endDate": "21/03/2019"
    }
}
```

## [](#recuperer-les-conflits-dexceptions)Récupérer les conflits d'exceptions

**'Post': {hemis\_base\_url}/zones/{zoneId}/agendas/{factorId}/overrides/conflicts**  
Pour effectuer cette requête, le factorId et le zoneId se passent en "path parameter" et le contenu de l'objet de l'exception est au format json dans le "body" de la requête.

Suite au refus d'ajout d'une exception, récupérer le contenu du json du corps à ajouter et le mettre ici.  
Cela vous retournera alors l'exception qui a la même priorité pour la même période.  
Dans le cas où vous voulez gérer les priorités de l'exception retournée causant un conflit, éditez l'exception ou supprimez la.

- - -

# [](#ambiance)Ambiance

Une ambiance permet de sauvegarder les valeurs des facteurs pour les zones auxquelles il est souhaitable de se rappeler de leurs différentes valeurs. Il est possible de les activer ou non.

[Documentation Swagger correspondante](https://developers.ubiant.com/swagger/hemis#/ambiances)

**Voici les différentes actions à effectuer sur les ambiances :**

## [](#creer-une-ambiance)Créer une ambiance

**'Post': {hemis\_base\_url}/ambiances**  
Pour effectuer cette requête le contenu de l'objet ambiance est au format json dans le "body" de la requête.

Dans un premier temps, pour ajouter une ambiance, il faut la nommer :

```
{
  "id": null,
  "name": "{ambianceName}",
  ...
}
```

Ensuite, il faut choisir un facteur environnemental ([liste des facteurs](/custom/factors)):

*   La température ("factorId": "TMP")
*   La luminosité ("factorId": "BRI")
*   L'occultation ("factorId": "BRIEXT")

```
{
  "id": null,
  "name": "{ambianceName}",
   "values": [
    {
      "factorId": "{factorId}",
      ...
    }
  ]
}

```

Puis il faut choisir une zone ([lister les zones](https://developers.ubiant.com/hemis/#lister-les-zones)):

```
{
  "id": null,
  "name": "AmbianceSalonTMP",
   "values": [
    {
      "factorId": "{factorId}",
      "zoneId": "{zoneId},
            "factorValue": null,
    }
  ]
}
```

Pour continuer, il faut récupérer l'actionneur qui va piloter le facteur environnemental et lui attribuer les valeurs: [lister les actionneurs d'un facteur environnemental d'une zone](https://developers.ubiant.com/hemis/#recuperer-la-liste-des-actionneurs)

```
{
  "id": null,
  "name": "{ambianceName}",
   "values": [
    {
      "factorId": "{factorId}",
      "zoneId": "{zoneId},
            "factorValue": null,
            "actuatorStates": {
                    "3697929#2": {
                        "type": "BASIC",
                        "itId": "ovp:%%1001-0142-9631%3697929",
                        "actuatorId": "{actuatorId}",
                        "value": 18.7,
                        "timeStamp": null,
                        "progressive": true,
                        "colorEnable": false,
                        "color": "#FFC697",
                        "hsvColor": [
                            0.07532051,
                            0.40784314,
                            1
                        ],
                        "ctEnable": false,
                        "ct": 3690,
                        "minActionValue": 7,
                        "maxActionValue": 30,
                        "remote": null,
                        "direct": true
                    }
                }
    }
  ]
}
```

Voici un exemple complet d'ajout d'ambiance au format json: [Ajouter une ambiance](/uploads/addambiance.json "Addambiance")

## [](#appliquer-une-ambiance)Appliquer une ambiance

**'Post': {hemis\_base\_url}/ambiances/{ambianceId}/apply**  
Pour effectuer cette requête le factorId, le zoneId et l'ambianceId se passe en "path parameter".

Applique une ambiance [créee](https://developers.ubiant.com/hemis/#creer-une-ambiance) selon sa zone et son facteur environnemental.

- - -

# [](#passerelle)Passerelle

Intéractions possibles avec les passerelles.

[Documentation Swagger correspondante](https://developers.ubiant.com/swagger/hemis#/gateways)

**Voici les différentes actions à effectuer sur les passerelles:**

## [](#ajouter-une-passerelle)Ajouter une passerelle

**'Post': {hemis\_base\_url}/WS\_GatewayManagement/add**  
Pour effectuer cette requête, l'identifiant de la passerelle (gatewayId) et son nom (gatewayName) doivent être passés en "x-www-form-urlencoded".

Pour trouver l'identifiant de la passerelle, il faut scanner le tag nfc de la passerelle pour qu'elle s'ajoute à la plateforme quickmove. Ensuite il est possible de retrouver son identifiant physique et son nom en la recherchant dans les objets. [Liens vers les objets quickmove](https://quickmove.ubiant.com/objects/)

- - -

# [](#objet-intelligent)Objet intelligent

Objet intelligent représente l'ensemble des objets intelligents installés dans l'Hemis. Ils peuvent être une passerelle, un interrupteur, un capteur, une ampoule, etc.

[Documentation Swagger correspondante](https://developers.ubiant.com/swagger/hemis#/intelligent-things)

**Voici les différentes actions à effectuer sur les objets intelligents:**

## [](#ajouter-un-objet-intelligent)Ajouter un objet intelligent

**'Post': {hemis\_base\_url}/intelligent-things**  
Pour effectuer cette requête, le contenu de l'objet "intelligent-things" est au format json dans le "body" de la requête.

Il faut préalablement connaitre l'identifiant de l'objet à ajouter présent sur celui-ci. Et le remplacer dans le champs "{idIt}". Ce champs est **obligatoire.**

```
{
    "id": "{idIt}"
}
```

## [](#ajouter-un-objet-intelligent-cas-de-lobjet-separable)Ajouter un objet intelligent (cas de l'objet séparable)

Le cas de l'objet séparable (reconnaissable par son type contenant le champs "splittable" à true) est de telle sorte qu'on l'ajoute module par module (hardware par hardware).  
C'est le cas de chaudière ou de relais 2 canaux qui permettent par exemple de les placer dans 2 zones différentes afin de séparer des éclairages.

La **première étape** est de récupérer les **hardwareTypesIds** de l'objet en effectuant la requête suivante:

**'Get': {hemis\_base\_url}/tags/{itId}/target**

La **deuxième étape** est d'ajouter les différentes parties de l'objet comme si c'était qu'un seul objet en effectuant la requête suivante en ajoutant la partie **hardwareCustomizations**:

**'Post': {hemis\_base\_url}/intelligent-things**  
Pour effectuer cette requête, le contenu de l'objet "intelligent-things" est au format json dans le "body" de la requête.

**Attention**, il faut ajouter l'objet en prenant son identifiant et en ajoutant un underscore, la lettre C suivi d'un numéro (itId\_C58).

```
{
    "id": "{itId_C1}",
    "hardwareCustomizations": [
                {
                    "hardwareTypeID": "{hardwareTypeID}"
                                }
                ]
}
```

Il faut alors réitérer l'étape 2 en changeant l'hardwareTypeId et l'itId pour le nombres de modules de l'objet.

## [](#recuperer-les-actionneurs-de-lobjet)Récuperer les actionneurs de l'objet

**'Get': {hemis\_base\_url}/intelligent-things/{itId}/actuators**  
Pour effectuer cette requête, remplacer "{itId}" par l'identifiant de l'objet souhaité.

Exemple de retour attendu (ici un relais):

```
[
    {
        "actuatorId": "id",
        "state": {
            "type": "BASIC",
            "itId": "id",
            "actuatorId": "id",
            "value": 0.0,
            "timeStamp": 1581413364193,
            "progressive": false,
            "colorEnable": false,
            "color": null,
            "hsvColor": null,
            "hue": null,
            "saturation": null,
            "ctEnable": false,
            "ct": null,
            "minActionValue": 0.0,
            "maxActionValue": 3.0,
            "remote": null,
            "direct": false,
            "transitionDuration": null
        },
        "hardwareState": {
            "type": "BASIC",
            "itId": "id",
            "actuatorId": "id",
            "value": null,
            "timeStamp": null,
            "progressive": false,
            "colorEnable": false,
            "color": null,
            "hsvColor": null,
            "hue": null,
            "saturation": null,
            "ctEnable": false,
            "ct": null,
            "minActionValue": 0.0,
            "maxActionValue": 3.0,
            "remote": null,
            "direct": false,
            "transitionDuration": null
        },
        "targetState": {
            "type": "BASIC",
            "itId": "id",
            "actuatorId": "id",
            "value": null,
            "timeStamp": null,
            "progressive": false,
            "colorEnable": false,
            "color": null,
            "hsvColor": null,
            "hue": null,
            "saturation": null,
            "ctEnable": false,
            "ct": null,
            "minActionValue": 0.0,
            "maxActionValue": 3.0,
            "remote": null,
            "direct": false,
            "transitionDuration": null
        },
        "actionningRepresentation": null,
        "itId": "id",
        "factors": [
            "TMP"
        ],
        "activated": true,
        "external_modification_forbidden": null,
        "com_type": "ONE_SHOT",
        "usableByUser": true,
        "sourceId": null
    },
    {
        "actuatorId": "id",
        "state": {
            "type": "BASIC",
            "itId": "id",
            "actuatorId": "id",
            "value": 0.0,
            "timeStamp": 1581413364217,
            "progressive": true,
            "colorEnable": false,
            "color": null,
            "hsvColor": null,
            "hue": null,
            "saturation": null,
            "ctEnable": false,
            "ct": null,
            "minActionValue": 0.0,
            "maxActionValue": 1.0,
            "remote": null,
            "direct": false,
            "transitionDuration": null
        },
        "hardwareState": {
            "type": "BASIC",
            "itId": "id",
            "actuatorId": "id",
            "value": null,
            "timeStamp": null,
            "progressive": true,
            "colorEnable": false,
            "color": null,
            "hsvColor": null,
            "hue": null,
            "saturation": null,
            "ctEnable": false,
            "ct": null,
            "minActionValue": 0.0,
            "maxActionValue": 1.0,
            "remote": null,
            "direct": false,
            "transitionDuration": null
        },
        "targetState": {
            "type": "BASIC",
            "itId": "id",
            "actuatorId": "id",
            "value": null,
            "timeStamp": null,
            "progressive": true,
            "colorEnable": false,
            "color": null,
            "hsvColor": null,
            "hue": null,
            "saturation": null,
            "ctEnable": false,
            "ct": null,
            "minActionValue": 0.0,
            "maxActionValue": 1.0,
            "remote": null,
            "direct": false,
            "transitionDuration": null
        },
        "actionningRepresentation": "REPEATER",
        "itId": "id",
        "factors": [
            "REPEATER"
        ],
        "activated": true,
        "external_modification_forbidden": null,
        "com_type": "ONE_SHOT",
        "usableByUser": true,
        "sourceId": null
    }
]
```

## [](#recuperer-les-capteurs-de-lobjet)Récuperer les capteurs de l'objet

**'Get': {hemis\_base\_url}/intelligent-things/{itId}/sensors**  
Pour effectuer cette requête, remplacer "{itId}" par l'identifiant de l'objet souhaité.

Exemple de retour attendu (ici un capteur de fluide):

```
[
    {
        "id": "id",
        "state": {
            "id": "FLUID_TMP",
            "value": null,
            "timestamp": 0,
            "oldValue": null,
            "evol": null,
            "feelingCoef": null,
            "hasAltSensor": false
        },
        "offset": 0.0,
        "activated": true,
        "monitoringRepresentation": null,
        "usableByUser": true
    }
]
```

## [](#ajouter-un-capteur-alternatif)Ajouter un capteur alternatif

**'Post': {hemis\_base\_url}/intelligent-things/alternativeSensor**  
Pour effectuer cette requête, l'identifiant de la zone courante (currentZoneId), l'identifiant du facteur (factorId) et la zone où les données vont être exportées (targetZoneId) doivent être passés en "x-www-form-urlencoded".

Permet d'ajouter un capteur.

## [](#activer-un-materiel)Activer un matériel

**'Post': {hemis\_base\_url}/intelligent-things/{itId}/hardware/{hardwareId}/activate**  
Pour effectuer cette requête, l'identifiant de l'objet intelligent (itId) et l'identifiant du matériel (hardwareId) doivent être passés en "path parameter".

Pour lister les identifiants des objets intelligents, voir [lister les objets intelligents](https://developers.ubiant.com/hemis/#lister-les-objets-intelligents).

Permet d'activer un matériel en fonction de l'identifiant de l'objet intelligent et du matériel.

## [](#desactiver-un-materiel)Désactiver un matériel

**'Post': {hemis\_base\_url}/intelligent-things/{itId}/hardware/{hardwareId}/deactivate**  
Pour effectuer cette requête, l'identifiant de l'objet intelligent (itId) et l'identifiant du matériel (hardwareId) doivent être passés en "path parameter".

Pour lister les identifiants des objets intelligents, voir [lister les objets intelligents](https://developers.ubiant.com/hemis/#lister-les-objets-intelligents).

Permet d'activer un matériel en fonction de l'identifiant de l'objet intelligent et du matériel.

- - -

# [](#apprentissage)Apprentissage

Apprentissage correspond à la partie "Learning".

[Documentation Swagger correspondante](https://developers.ubiant.com/swagger/hemis#/learning)

**Voici les différentes actions à effectuer sur l'apprentissage':**

## [](#recuperer-les-predictions-dun-parametre-choisit)Récupérer les prédictions d'un paramètre choisit

**'Get': {hemis\_base\_url}/learning/prediction/{zone}/{factorId}/{granularity}/{date}**  
Pour effectuer cette requête, le nom de la zone, le facteur environnemental (factorId), la granularité et la date doivent être passés en 'path parameter'.

Permet de récupérer les données de prédictions d'un facteur environnemental pour une zone en fonction de sa granularité (DAY, WEEK, MONTH, YEAR) et d'une date en millisecondes.

## [](#recuperer-un-ensemble-de-predictions-pour-un-ensemble-de-parametres-choisits)Récupérer un ensemble de prédictions pour un ensemble de paramètres choisits

**'Post': {hemis\_base\_url}/learning/prediction**  
Pour effectuer cette requête, le contenu de l'objet prediction est au format json.

Exemple de contenu:

```
[
  {
    "granularity": "YEAR",
    "date": 0,
    "factorId": "TMP",
    "zone": "salon"
  }
]
```

Permet de récupérer un ensemble de prédictions pour un ensemble de paramètres choisits.

- - -

# [](#facteur)Facteur

Facteur correspond aux capteurs mis en place dans l'Hemis.

[Documentation Swagger correspondante](https://developers.ubiant.com/swagger/hemis#/factors)

**Voici les différentes actions à effectuer sur les capteurs:**

## [](#changer-la-valeur-des-parametres-dun-facteur-environnemental)Changer la valeur des paramètres d'un facteur environnemental

**'Put': {hemis\_base\_url}/WS\_ReactiveManagement/{zoneId}/settings/{factorId}/value**

Pour effectuer cette requête, l'identifiant de la zone (zoneId) et l'identifiant du facteur environnemental (factorId) doivent être passés en 'path parameter'. La valeur a attribuer (value) doit être passée en "x-www-form-urlencoded".

Il faut choisir une zone ([lister les zones](https://developers.ubiant.com/hemis/#lister-les-zones)) et un facteur environnemental ([liste des facteurs](/custom/factors)) puis lui attribuer une valeur.

Pour vérifier si la valeur a bien était attribuée, [lister les valeurs](https://developers.ubiant.com/hemis/#lister-les-valeurs-attribu%C3%A9es-dun-facteur-environnemental).

- - -

# [](#scenario)Scenario

Scenario correspond aux alertes et aux objectifs de la consommation de l'Hemis.

[Documentation Swagger correspondante](https://developers.ubiant.com/swagger/hemis#/scenario)

**Voici les différentes actions à effectuer sur les scenarios:**

## [](#recuperer-les-anomalies-detectees)Récupérer les anomalies détectées

Permet de récupérer toutes les anomalies générées dans les dernières 24h. Aujourd'hui, permet seulement de récupérer des anomalies permettant de détecter un retard ou une incapacité à atteindre l'objectif de température en phase de chauffe (Heating Phase Anomaly Detection Objective : HPADO).

**'Get': {hemis\_base\_url}/WS\_ScenarioManagement/anomalies**

Il est possible de filtrer les anomalies à l'aide d'un "query parameter" sur les notions suivantes:

*   Zone: les anomalies détectées sur une zone spécifique à l'aide de son identifiant (name).
*   Factor: les anomalies détectées sur un facteur environnemental spécifique à l'aide de son identifiant ([liste des facteurs](/custom/factors)).
*   Tags: les anomalies détectées sur un tag spécifique (actuellement parmis : "Actionning", "Scenarios", ou "HPADO").

## [](#creer-une-alerte)Créer une alerte

**'Post': {hemis\_base\_url}/WS\_ScenarioManagement/alerts**  
Pour effectuer cette requête le contenu de l'objet alerte est au format json dans le "body" de la requête.

Dans un premier temps, pour ajouter une alerte il faut choisir un facteur environnemental ([liste des facteurs](/custom/factors)):

*   La température ("factorId": "TMP")
*   La luminosité ("factorId": "BRI")
*   L'occultation ("factorId": "BRIEXT")

```
{
  "id": null,
  "factorId": "{factorId}",
    ...
}
```

Puis il faut choisir une zone ([lister les zones](https://developers.ubiant.com/hemis/#lister-les-zones)):

```
{
   "id": null,
  "factorId": "{factorId}",
    "zoneId": "{zoneId}",
    ...
}
```

De plus il faut attribuer les valeurs de l'alerte:

```
{
  "id": null,
  "factorId": "{factorId}",
  "zoneId": "{zoneId}",
  "enable": true,
  "minTimeBetweenExecution": 1800000,
  "condition": {
    "type": "OUT_INTERVAL",
    "value1": 10,
    "value2": 35
  },
  ...
}
```

Pour finir il faut choisir le type de l'alerte, Notification (NOTIFICATION) ou Push notification (PUSH\_NOTIF).

```
{
  "id": null,
  "factorId": "TMP",
  "zoneId": "Salon_8lvnor1l",
  "enable": true,
  "minTimeBetweenExecution": 1800000,
  "condition": {
    "type": "OUT_INTERVAL",
    "value1": 10,
    "value2": 35
  },
  "actions": [
    {
      "type": "NOTIFICATION",
      "target": null
    },
    {
      "type": "PUSH_NOTIF",
      "target": "2c91808365f94f3e01660aa3a0050372"
    }
  ]
}
```

## [](#ajouter-un-nouveau-scenario-de-consommation-annuelle)Ajouter un nouveau scénario de consommation annuelle

**'Post': {hemis\_base\_url}/​WS\_ScenarioManagement/alerts**  
Pour effectuer cette requête le contenu de l'objet goal est au format json dans le "body" de la requête.

Dans un premier temps, pour ajouter un objectif de consommation il faut choisir un facteur environnemental ([liste des facteurs](/custom/factors)):

*   La consommation électrique ("factorId": "CPOW")

```
{
    "factor": "{factorId}",
    ...
}
```

Ensuite il faut indiquer la consommation annuelle passée, l'objectif en pourcentage ou en coût, la date du début de l'objectif.  
Exemple avec une ancienne consommation de 9000 kWh avec un objectif de 10% pour le facteurEnvironnemental de l'énergie (CPOW).

```
{
    "factor": "CPOW",
    "lastYearConsumption": 9000,
    "goal": 8100,
    "percent": true,
    "cost": false,
    "beginDate": 1552993200000,
    "beginIndex": 8774.82,
    "currentIndex": null,
    "currentIndexDate": null,
    "proposedUpdateDate": null,
    "objRemainingPrediction": null
}
```

## [](#activer-desactiver-une-alerte-specifique-par-son-identifiant)Activer/désactiver une alerte spécifique par son identifiant

**'Put': {hemis\_base\_url}/WS\_ScenarioManagement/alerts/{alertId}/enable**  
Pour effectuer cette requête, l'identifiant de l'alerte (alertId) doit être passé en 'path parameter'. Le champs "enable" doit être passé en "x-www-form-urlencoded".

Permet d'activer ou de désactiver une alerte par le biais de son identifiant.. Pour récupérer un identifiant d'alerte voir la [liste des alertes](https://developers.ubiant.com/hemis/#lister-les-alertes).

- - -

# [](#tag)Tag

Les Tags permettent d'associer des puces NFC ou des QRCodes à une cible.  
Les cibles peuvent caractèriser une zone, un objet, une passerelle, un évènement, une clé, une ambiance ou un batîment.  
Un tag de **zone** ou de **bâtiment** permet de rentrer directement dans la zone ou la bâtiment.  
Un tag d'**objet** ou de passerelle permet d'identifier l'objet / passerelle afin de l'ajouter dans l'Hemis désiré via Quickmove, la base de recensemment des objets.  
Un tag dit d'**évènement** permet d'associer un évènement comme éteindre la lumière (BRI\_ON). Il est alors possible au moment de l'analyse du tag, d'associer la requête avec la zone où le tag s'est effectué et d'injecter l'évènement dans cette zone.  
La liste d'évènements est disponnible dans la partie système ainsi que leurs explications et comment est-il possible de les injecter : [Evènements](https://developers.ubiant.com/hemis#injecter-un-evenement)  
Un tag d'**ambiance** permet d'associer une ambiance préalablement sauvegardée.  
Un tag de **clé** permet de donner des droits à un Hemis.

[Documentation Swagger correspondante](https://developers.ubiant.com/swagger/hemis#/tags)

**Voici les différentes actions à effectuer sur les tags :**

## [](#ajouter-modifier-un-tag)Ajouter/Modifier un tag

**'Post': {hemis\_base\_url}/tags**

L'ajout d'un tag se fait par le biais d'un objet au format Json.

```
{
    "tagType": "NFC",
    "targetType": "ZONE",
    "targetId": "salonId",
    "label": "tagSalon",
    "modifable": true
}
```

Explication des champs :

*   Type du tag (**tagType**), peut être QRCode ou NFC.
*   Cible du tag (**targetType**), peut être ZONE, IT, GATEWAY, EVT, EMPTY, HEMISKEY, AMBIANCE, BUILDING, NONE.
*   L'identifiant de la cible (**targetId**), peut être par exemple l'identifiant de la zone pour un tag de type zone.
*   Le label (**label**) permet de donner un nom au tag (**label**).
*   Le champ modifable (**modifable**) permet de notifier si un tag est modifiable ou non, il est modifiable par défaut.

**'Put': {hemis\_base\_url}/tags/{tagId}**

La modification d'un tag se fait comme l'ajout d'un tag en mentionnant l'identifiant de celui-ci (\*_tagId_) dans l'url de la requête.

## [](#changer-supprimer-limage-dun-tag)Changer/Supprimer l'image d'un tag

**'Put': {hemis\_base\_url}/tags/{tagId}/image**

L'ajout de l'image d'un tag se fait par le biais d'un form-data en indiquant l'identifiant du tag (**tagId**) dans l'url de la requête.  
Il faut ajouter un champ **image** et upload celle-ci en tant que valeur.

**'Delete': {hemis\_base\_url}/tags/{tagId}/image**

La suppression de l'image d'un tag se fait simplement en mentionnant l'identifiant du tag (tagId) dans l'url de la requête.

- - -

# [](#tarification)Tarification

La Tarification permet d'évaluer les tarifs de consommation selon un facteur environnemental afin de connaître le coût de sa consommation. Il est possible alors de prédire, fixer un objectif ou faire une simulation de tarification.

[Documentation Swagger correspondante](https://developers.ubiant.com/swagger/hemis#/tarification)

**Voici les différentes actions à effectuer sur les tarifications**

## [](#ajouter-une-tarification)Ajouter une tarification

**'Post': {hemis\_base\_url}/tarifications**  
Pour effectuer cette requête le contenu de l'objet tarification est au format json dans le "body" de la requête.

Dans un premier temps, pour ajouter une tarification, il faut choisir le type de tarification à mettre en place et ainsi récupérer son identifiant disponnible dans le tableau ci-dessous:

| Tarification | Identifiant | Description |
| --- | --- | --- |
| Base | TH  | Toutes les heures |
| Heures creuses | HC  | Heures creuses |
| Heures pleines | HP  | Heures pleines |
| Heures normales | HN  | Heures normales |
| Heures de pointe mobile | PM  | Heures de pointe mobile |
| Bleu HC | HCJB | Heures creuses pour les jours bleus |
| Blanc HC | HCJW | Heures creuses pour les jours blancs |
| Rouge HC | HCJR | Heures creuses pour les jours rouges |
| Bleu HP | HPJB | Heures pleines pour les jours bleu |
| Blanc HP | HPJW | Heures pleines pour les jours blancs |
| Rouge HP | HPJR | Heures pleines pour les jours rouges |
| Heures week-end | HWE | Heures week-end |
| Heures semaines | HS  | Heures semaines |

Pour une explication plus détaillée de la tarification par tempo, voir [l'explication du site de Selectra.](https://selectra.info/energie/fournisseurs/edf/tempo)

Il faut ensuite choisir:

*   le nom de la tarification
*   un facteur environnemental, comme l'électricité (CPOW). Voir [liste des facteurs](/custom/factors)
*   une unité monétaire, comme l'euro (EUR)
*   une unité du facteur, comme kWh pour l'électricité
*   une date d'activation de la tarification en millisecondes
*   l'identifiant de la zone à appliquer la tarification
*   le champs actual doit rester à true si vous voulez que votre tarification soit ajoutée, sinon elle permet de faire des simulations de tarification

De plus, il faut ajouter la liste des tarifs:

*   Partial représente un intervalle à définir. Par exemple que le tarif soit applicable pour certaines heures
*   Absolute représente un intervalle fixe entre deux dates

Et ensuite ajouter le prix de la tarification dans le champ **value**.

Et enfin un champ **infos** est présent afin de sauvegarder les informations supplémentaires de cas particuliers:

| Information | Signification |
| --- | --- |
| YFC | Coût fixe à l'année |
| PRO | Identifiant du fournisseur |
| OFF | Nom de l'offre commerciale |
| OPT | Nom de l'option souscrite |
| POW | Capacité du compteur |
| HC\_"tarif\_name" | "tarif\_name" est un tarif d'heure creuse |
| IND | True si la tarification est indéterministe |

Voici un exemple du corps de la requête à injecter pour un intervalle d'heure d'une journée.

```
{
    "id": null,
    "actual": true,
    "name": "firstTarification",
    "factor_id": {
        "factor": "CPOW",
        "zoneName": "MyHemis"
    },
    "date_of_activation": 1553012560791,
    "currency_unit": "EUR",
    "factor_unit": "kWh",
    "tarifs_list": [
        {
            "provider_id": "HP",
            "name": "Heure Pleine",
            "value": 0.1593,
            "time_constraint": {
                "partials_list": [
                    {
                        "fields_list": {
                            "HOUR_OF_DAY": {
                                "match_values": [
                                    7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22
                                ]
                            }
                        }
                    }
                ],
                "absolutes_list": []
            }
        }
    ],
    "infos": {
        "OPT": "Heures Creuses",
        "POW": "9kVA",
        "PRO": "EDF",
        "OFF": "Tarif Bleu"
    }
}
```

Voici un exemple du corps de la requête à injecter pour un intervalle entre deux dates données.

```
{
  "id": null,
  "actual": true,
  "name": "thirdTarification",
  "factor_id": {
    "factor": "CPOW",
    "zoneName": "MyHemis"
  },
  "date_of_activation": 1,
  "currency_unit": "EUR",
  "factor_unit": "kWh",
  "tarifs_list": [
    {
      "provider_id": "HP",
      "name": "Heure Creuses",
      "value": 0.1295,
      "time_constraint": {
        "partials_list": [
        ],
        "absolutes_list": [
        	{
        		"begin": 123132132136,
        		"end": 1231651165
        	}
        ]
      }
    }
  ],
  "infos": {
  }
}
```

- - -

# [](#utilisateur)Utilisateur

Users permet de récupérer le session\_token de l'Hemis, utilisé pendant la phase d'authentification préalablement faite.

[Documentation Swagger correspondante](https://developers.ubiant.com/swagger/hemis#/users)

**Voici l'action à effectuer sur l'utilisateur:**

## [](#sidentifier)S'identifier

**'Post': {hemis\_base\_url}/WS\_UserManagement/login**  
Pour effectuer cette requête, l'email, le password et le kernelId doivent être passés en "x-www-form-urlencoded".

Permet de récupérer le session token afin de s'identifier. Pour plus de détails voir la [partie authentification](https://developers.ubiant.com/tutoriels/authentification).

- - -

# [](#zones)Zones

Une zone correspond à une pièce de l'Hemis.

[Documentation Swagger correspondante](https://developers.ubiant.com/swagger/hemis#/zones)

**Voici les différentes actions à effectuer sur les zones :**

## [](#ajouter-modifier-une-zone)Ajouter/Modifier une zone

**'Post': {hemis\_base\_url}/zones**

L'ajout d'une zone se fait par le biais d'un objet au format Json.

```
{
    "name": "Salon",
    "type": "Salon",
    "surface": "52.0",
    "external": true,
    "floor": 1,
    "parentId": "grandSalonId"
}
```

Explication des champs:

*   Nom de zone (**name**). Seul ce champs est obligatoire pour créer une zone.
*   Type de zone (**type**). Le type de la zone permet d'identifier au niveau de l'application quel type de zone est souhaité afin d'obtenir l'image par défaut de celle-ci. L'image est modifiable par après, ce champs n'est donc pas obligatoire. L'explication pour modifier l'image d'une zone est disponnible ici.  
    Les types connus sont actuellement: Chambre, Cuisine, Salon, Hall, Salle\_de\_bain, Bureau, Garage, Couloir, Salle\_de\_jeu, Salle\_de\_lavage, Chaufferie, Toilettes, Vestibule, Atelier, Cave\_a\_vin, Autre, Canteen, Gym, Locker\_room, Library, Amphitheater, Classroom, Staircase, Meeting\_room, Cellar, Salle\_a\_manger, Entree, Terrasse, Cuisinette, Local\_photocopie, Annexe, Bibliotheque, Depot, Dortoir, Preau, Refectoire, Salle\_Classe, Salle\_Informatique, Salle\_Profs, Floor et Hemis.
*   Surface de la zone (**surface**). La surface de la zone est en mètre carré (m²).
*   Zone externe (**external**). La zone peut-être exclue en mentionnant le champs external à true afin de ne pas perturber les calculs fait par Hemis. Par exemple, un balcon extérieur content des capteurs de température devrait être exclu.
*   L'étage de la zone (**floor**). L'étage de la zone permet d'identifier au niveau de l'application où ce situe la zone pour le rendement en 3 dimensions.
*   La zone parente (**parentId**). Non mentionnée, elle sera par défaut mise sous "MyHemis". Par exemple, il est possible d'éteindre la lumière de toutes les zones sous "MyHemis" en allant dans celle-ci. Il est possible de changer la zone parente par une autre zone en indiquant son identifiant.

Les champs retournés par la requête et non modifiable sont:

*   L'identifiant de la zone (**id**).
*   La zone possède une image changée par l'utilisateur (**hasImage**). Si hasImage est à true, c'est à dire que l'image a été modifiée et l'image par défaut du type de la zone n'est plus utilisée.
*   La zone est une zone parente (**metazone**).

**'Put': {hemis\_base\_url}/zones/{zoneId}**

La modification d'une zone se fait comme l'ajout d'une zone en mentionnant l'identifiant de celle-ci (**zoneId**) dans l'url de la requête.

## [](#changer-supprimer-limage-dune-zone)Changer/Supprimer l'image d'une zone

**'Put': {hemis\_base\_url}/zones/{zoneId}/image**

L'ajout de l'image d'une zone se fait par le biais d'un form-data en indiquant l'identifiant de la zone (**zoneId**) dans l'url de la requête.  
Il faut ajouter un champ **image** et upload celle-ci en tant que valeur.  
La zone aura son champ hasImage qui passera à true.

**'Delete': {hemis\_base\_url}/zones/{zoneId}/image**

La suppression de l'image d'une zone se fait simplement en mentionnant l'identifiant de la zone (zoneId) dans l'url de la requête.  
La zone aura son champ hasImage qui passera à false et l'image par défaut du type sera alors utilisée ou l'image par défaut sans type si la zone n'a pas de type.

## [](#recuperer-linertie-apprise-de-la-temperature-dune-zone)Récupérer l'inertie apprise de la température d'une zone

**'Get': {hemis\_base\_url}/zones/{zoneId}/getLearnedTmpInertia**

Retourne les valeurs d'inertie apprises sous-forme de tableau de 4 valeurs (en °C/min):

| Valeur | Signification | Description |
| --- | --- | --- |
| 0   | Rising/Active | Vitesse d'élévation de la température quand le système est actif (chauffage) |
| 1   | Falling/Active | Vitesse de baisse de la température quand le système est actif (climatisation) |
| 2   | Rising/Passive | Vitesse d'élévation de la température quand le système est passif (apports externes) |
| 3   | Falling/Passive | Vitesse de baisse de la température quand le système est passif (pertes) |

## [](#ajouter-un-lien-de-zone-disponnible-depuis-la-version-d-hemis-1-10-0)Ajouter un lien de zone (disponnible depuis la version d'Hemis 1.10.0)

Il existe différent type de lien de zone:

\-les liens de type **Hemis** qui caractèrisent les liens entre zones de différents Hemis.  
\-les liens de type **Source**, qui caractèrisent les liens entre zone source et zone contrôlée.

### [](#lien-de-type-hemis)Lien de type Hemis

**'Post': {hemis\_base\_url}/zones/{zoneId}/links**

L'ajout du lien se fait par le biais d'un objet au format Json. De plus, il faut mentionner la zone correspondante dans l'url de la requête.

```
{
    "type": "HEMIS",
    "direction": "IMPORTED",
    "buildingId": "1234",
    "zoneId": "test",
    "token": "super-secure-token",
    "includedFactors": [],
    "excludedFactors": []
}
```

Explication des champs:

*   Type du lien (**type**). Cette valeur doit être impérativement "HEMIS" dans le cas d'un lien de type Hemis.
*   Direction du lien (**direction**). Cette valeur doit être "IMPORTED" ou "EXPORTED". Cela permet de déterminer le sens du lien. L'hemis parent aura un lien avec une direction "IMPORTED".
*   L'identifiant du bâtiment (**buildingId**) auquel la zone est liée.
*   L'identifiant de la zone (**zoneId**) à laquelle la zone portant ce lien est liée.
*   Facteur à exporter (**includedFactors**) est une liste des facteurs à exporter. Attention, ceci est uniquement pris en compte pour les liens de direction "EXPORTED". Ne peut être définit en même temps que **excludedFactors**.
*   Facteurs à ne pas exporter (**excludedFactors**) est une liste des facteurs à ne pas exporter. Attention, ceci est uniquement pris en compte pour les liens de direction "EXPORTED". Ne peut pas être définit en même temps que **includedFactors**.
*   Token (**token**) permet de spécifier un token pour l'authentification des bâtiments entre eux. Si renseigné, ce token doit être le même sur les deux liens respectifs. Si non renseigné, l'authentification sera basée sur l'échange de tokens JWT générés par hémisphère pour chacun des bâtiments.

### [](#lien-de-type-source)Lien de type Source

**'Post': {hemis\_base\_url}/zones/{zoneId}/links**

Comme pour les liens de type Hemis, les liens de type Source se font par le biais de la même requête, seul le champs **type** permet de différencier le cas d'un lien de type Hemis d'un lien de type Source.

```
{
    "type": "SOURCE",
    "sourceZoneId": "test",
        "factor": "TMP",
        "importedFactor": "FLUID_TMP"
}
```

Explication des champs:

*   Type du lien (**type**). Cette valeur doit être impérativement "SOURCE" dans le cas d'un lien de type Source.
*   L'identifiant de la zone source (**sourceZoneId**) auquel la zone contrôlée est liée.
*   Le facteur du lien (**factor**) est le facteur environnemental du lien entre les zones.
*   Le facteur importée du lien (**importedFactor**) est le facteur environnemental importé du lien entre les zones.

- - -

# [](#compte)Compte

La partie compte correspond principalement à la gestion des comptes tiers, overkiz et philips hue de l'Hemis.

[Documentation Swagger correspondante](https://developers.ubiant.com/swagger/hemis#/accounts)

**Voici les différentes actions à effectuer sur les comptes:**

## [](#ajouter-un-compte)Ajouter un compte

**'Post': {hemis\_base\_url}/WS\_AccountManagement/{accountType}**  
Pour effectuer cette requête, le type de compte (accountType) doit être passé en "path parameter".

Les types de comptes actuellement disponnibles sont: netatmo, myfox (somfy), google (google home), zipato et obix.  
Prochaine disponnibles: Enedis, Sonos et Amazon (Alexa) (édité le 26/03/2019).

- - -

# [](#connecteur)Connecteur

La partie connecteur correspond à la modélisation des réseaux et cablâges dans le système.

Pour ce faire il y a 3 nouveaux concepts :

*   les **connecteurs** (modélisation des réseaux (elec, logique,...)
*   les **slots** (imbrication, regroupement d'objet)
*   les **liens** entre objets

### [](#les-connecteurs)Les connecteurs

Les connecteurs peuvent se situer à différents niveaux d'un objet : soit au niveau de l'objet lui même, soit au niveau d'un slot de l'objet ou au niveau d'un hardware de l'objet. Chaque connecteurs est typé (energy, control, c'est libre pour l'instant), possède un nom unique et possède un sens (master/slave). Les liens peuvent se faire entre 2 connecteurs de même type, et en respectant le sens master/slave.

**exemple 1:**

Un luminaire possède un connecteur esclave de type électrique pour modéliser son alimentation esclave. Un disjoncteur possède deux connecteurs électriques: un maître et un esclave pour modéliser respectivement sa sortie et son alimentation. Les disjoncteurs peuvent ainsi être chaînés et le connecteur d’un luminaire peut être lié au connecteur maître du disjoncteur.

**exemple 2:**

Le disjoncteur possède un connecteur esclave de type contrôle correspondant à sa remontée d’état. Ce connecteur peut ainsi être raccordé à un des connecteurs maître d’un automate qui sera responsable de sa relève. L’automate possède un connecteur contrôle esclave qui pourra être relié au connecteur contrôle maître d’une passerelle Ubiant.

### [](#les-slots)Les slots

L’imbrication physique d’objet et leur position respective (cas des armoires électriques qui contiennent des disjoncteur, passerelles, compteurs, etc…) sera modélisée par le concept de slot (emplacement).  
Les slots se situent au niveau d'un objet. On peut déclarer dans le type une nouvelle propriété qui indique que l'objet peut en recevoir d'autre.

**exemple 1:**

Une passerelle WIT peut recevoir jusqu'à 6 plugs. On peut modéliser le type de la passerelle WIT en un objet comportant 6 slots pouvant recevoir chacun un objet plug.

**exemple 2 :**

On modélise une armoire électrique par un objet comportant une liste non finie de slot. Ça nous permettra par la suite de localiser physiquement les objets qui y sont.

[Documentation Swagger correspondante](https://developers.ubiant.com/swagger/hemis#/connector%20link)

**Voici les différentes actions à effectuer sur les connectors:**

## [](#ajouter-un-connecteur)Ajouter un connecteur

**'Post': {hemis\_base\_url}/WS\_ConnectorLinkManagement**  
Pour effectuer cette requête, l'identifiant du connecteur esclave, l'identifiant du connecteur master, la representation du code du lien et la réfèrence du lien doivent être passés en "form data".

Les identifiants des connecteurs proviennent du type de l'objet. La représentation du code permet à Designer d'identifier de son côté le lien et la réfèrence du lien est normée afin de pouvoir représenter le lien (cable, elec, control...)

- - -

# [](#system)System

System correspond à la partie système de l'Hemis. Il est possible par exemple d'injecter un évènement dans une zone ou exporter ses données minimisées sous forme d'un fichier.

[Documentation Swagger correspondante](https://developers.ubiant.com/swagger/hemis#/system)

## [](#injecter-un-evenement)Injecter un évènement

**'Post': {hemis\_base\_url}/WS\_SystemManagement/{zoneId}**

Pour injecter un évènement, il est nécessaire de mentionner l'identifiant de la zone (**zoneId**) dans l'url de la requête.  
De plus il faut mentionner le type d'évènement à injecter.

Voici une liste des évènements injectables:

| Event | Description |
| --- | --- |
| ALARM\_ON | Alarme activée |
| ALARM\_OFF | Alarme désactivée |
| ALARM\_PARTIAL | Alarme partielle |
| ALERT\_1 | Alerte |
| BRI\_ON | Luminosité activée |
| BRI\_OFF | Luminosité désactivée |
| BRI\_ON\_SWS | Luminosité activée en remote |
| BRI\_OFF\_SWS | Luminosité désactivée en remote |
| BRI\_AUTO | Luminosité automatique |
| BRIEXT\_ON | Luminosité extérieure activée |
| BRIEXT\_OFF | Luminosité extérieure désactivée |
| BRIEXT\_ON\_SWS | Luminosité extérieure activée en remote |
| BRIEXT\_OFF\_SWS | Luminosité extérieure désactivée en remote |
| BRIEXT\_AUTO | Luminosité extérieure automatique |
| BRIEXT\_STOP | Luminosité extérieure arrêtée |
| CPOW\_EVT | Evènement de consomation électrique |
| FEELTMP\_ON | Température ressentie activée |
| FEELTMP\_INC | Température ressentie incrémentée |
| FEELTMP\_DEC | Température ressentie décrémentée |
| FEELTMP\_RESET | Température ressentie restaurée |
| FEELBRI\_ON | Luminosité ressentie activée |
| FEELBRI\_INC | Luminosité ressentie incrémentée |
| FEELBRI\_DEC | Luminosité ressentie décrémentée |
| IPOW\_EVT | Evènement de consomation électrique instantannée |
| LUMINION\_ALERT | Luminion alerte |
| LUM\_OFF | Eteindre le luminion |
| ON  | Activé |
| OFF | Désactivé |
| ON\_SWS | Activé en remote |
| OFF\_SWS | Désactivé en remote |
| TMP\_ON | Température activée |
| TMP\_OFF | Température désactivée |
| TMP\_ON\_SWS | Température activée en remote |
| TMP\_OFF\_SWS | Température désactivée en remote |
| TMP\_AUTO | Température automatique |

- - -

# [](#data-provider)DataProvider

Ce service est le point d'accès unique à toutes les données de type _séries temporelles_ dans un Hemis.

[Documentation Swagger correspondante](https://developers.ubiant.com/swagger/hemis#/data)

## [](#series-temporelles)Séries temporelles

**Ce que sont les séries temporelles (_time series_)**

Il s'agit des données historisées (valeur + date) correspondant à une suite de points (_timepoints_), dont on conserve l'évolution au cours du temps en base de données. Dans Hemis, il peut s'agir des relevés des capteurs et des facteurs environnementaux, de l'état des actionneurs, etc. Toute série temporelle est identifiée par la source unique qui la produit et possède donc un identifiant unique (_dataSourceID_). En plus de ça, une série temporelle est décrite par un ensemble de caractéristiques (_tags_). Ce sont des méta-données qui décrivent les séries et peuvent servir à filtrer les données lors des requêtes.

La base de données utilisée est une base de données spécialisée pour les séries temporelles (_TSDB : Time Series Database_), optimisée pour stocker et requêter une masse importante de ce type de données.

**Ce que ne sont pas les séries temporelles**

Le DataProvider n'est pas concerné par les données structurelles, c'est-à-dire le modèle d'Hemis. Le stockage des _zones_, des _objets_, des _scénarios_, des _objectifs_, des _agendas_, etc. n'est pas lié au DataProvider. Ces données-là demeurent stockées dans la base de données relationnelle et sont accessibles par les Web services correspondants comme avant.

## [](#la-politique-de-retention)La politique de rétention

Les séries ne sont pas toutes conservées en temps réel jusqu'à l'infini car, il n'est pas nécessaire de conserver toutes chaque donnée de la même façon. Par exemple, pour certaines séries on va garder le temps réel sur 1 an, puis une valeur par heure pendant 5 ans, tandis que pour d'autre on ne gardera qu'une semaine de temps réel et 1 an de valeurs par heure.  
Ces différentes stratégies de conservation des données sont appelées _politiques de rétention_ et sont modélisées par un objet : _DataPersistenceDescription_. Toutes les séries possédant un même _DataSourceType_ (triplet Nature+Group+CPID) possède un même _DataPersistenceDescription_, cela signifie qu'elles sont donc conservées de la même façon au fil du temps.

## [](#modelisation)Modélisation

### [](#les-tags)Les Tags

*   _Measurement_ : décrit la grandeur (ou le type) de la mesure et y associe une unité _measurementUnit_ (ex. température en °/C, intensité d'action en %) (NB: pour les données non numériques, il n'y a pas d'unités)
*   _Nature_ : décrit la nature de la source :
    *   _SEN_ : capteur
    *   _ACT_ : actionneur
    *   _FACT_ : facteur environnemental
    *   _PRED_ : prévisions/estimations issus des algos de _machine learning_
    *   _EXT_ : source de données externe (ex. APIs : _OWM_, _Enedis_, etc.)
    *   _IT_ : objet (Intelligent Thing)
    *   _TAR_ : target
*   _Group_ : décrit un sous-ensemble logique au sein d'un même measurement (ex. _TMP_ et _VALVE\_TMP_ au sein du Measurement Température(_TEMP_)) ; cela correspond le plus souvent à l'identifiant d'un facteur environnemental.
*   _Zone_ : La zone dans laquelle cette série est mesurée **ou** _outside_ pour les données extérieures au bâtiment (p. ex. météo) **ou** un composant d'un IT State (nature:IT / Group : C\_STATE) (ex. zone=PAIR\_ST (pairing state)) \[Dans ce cas la zone est utilisée comme un un sous-groupe pour un objectif d'optimisation et car on considère que la data est propre à un IT, peu importe la zone ou il se trouve.\]
*   _CPID_ : ID spécial pour des séries qu'on désire conserver de façon spécifique, différente des autres séries qui ont le même couple _Nature_\-_Group_.
*   _DataSourceID_ : Il s'agit de l'ID unique de la source. (si c'est un matériel, ex. capteur, il s'agit de son ID Hemis (_sensorID_))

### [](#les-fields)Les Fields

Un point (_timepoint_) d'une série temporelle ne contient pas une unique valeur à une date _d_, mais peut en contenir plusieurs.

*   Pour les séries temps réel :
    *   _VALUENB_ : nombre (valeur mesurée)
    *   _VALUESTR_ : chaîne de caractère (valeur mesurée)
    *   _RELIABILITY_ : indice \[0,1\] représentant la fiabilité de cette mesure
*   Pour les synthèses sur un intervalle de temps (_données aggrégées_ ex. Par heure) :
    *   _MINIMUM_ : minimum des points (_VALUENB_ ou _MINIMUM_) sur l'intervalle
    *   _MAXIMUM_ : maximum des points (_VALUENB_ ou _MAXIMUM_) sur l'intervalle
    *   _AVERAGE_ : moyenne des points (_VALUENB_ ou _AVERAGE_) sur l'intervalle
    *   _DIFF_ : écarts entre les points consécutifs (_MAXIMUM_\-_MINIMUM_) sur l'intervalle
    *   _SUM_ : somme des points (_DIFF_) sur l'intervalle
    *   _MAXIMUMOCC_ : valeur la plus fréquente (_VALUESTR_ ou _MAXIMUMOCC_) sur l'intervalle
    *   _LAST_ : dernière valeur dans l'ordre chronologique (_VALUESTR_ ou _LAST_) sur l'intervalle
    *   _RELIABILITY_ : indice \[0,1\] représentant la fiabilité du point
    *   _NBPOINT_ : nombre de points aggrégés sur l'intervalle

N.B. : Un point temps réel contient soit _VALUENB_ soit _VALUESTR_ mais pas les deux, idem pour les synthèses qui en sont issues.

N.B. : Certaines séries n'ont pas de temps réel, elles sont directement persistées en synthèses (p. ex. data de consommation externes importées depuis l'API Enedis).

### [](#les-syntheses)Les synthèses

**Principe**

Les données temps réel synthétisées sur un intervalle de temps prennent la forme de une ou plusieurs valeurs résultant d'une formule appliquée sur toutes les valeurs de cet intervalle.  
Par exemple le field _AVERAGE_ obtenu en faisant une requête de _granularity_\=3600 (par heure) sera la valeur moyenne de tous points présents (c-à-d de leur _field_ _VALUENB_) sur chaque intervalle d'une heure.

_**Offset**_

Un intervalle, par exemple une heure, peut être borné de différentes façons. Pour les heures, un bornage classique utilisé est le découpage en heure pleines. Pour les jours cela peut être en commençant à 00:00:00 de la timezone du bâtiment, et en finissant à 23:59:59. On appelle _offset_ ce découpage des intervalles entre des bornes choisies. Si on fait une requête sans spécifier de _beginDate_, le découpage sera arbitrairement basé sur la date de la requête. Afin d'obtenir un découpage précis, on spécifie une _beginDate_ calée sur les bornes désirées. Par exemple, pour avoir les synthèses sur les heures pleines, on doit spécifier une beginDate de la forme : _xx:00:00.000_.

N.B. : Les séries sont automatiquement pré-synthétisées en _granularity=3600_ (heure) et _granularity=86400_ (jour) dans l'offset correspondant au heures pleines et aux jours pleins de la timezone. Par conséquent, lorsqu'on fait des requêtes dans ces granularités, il est bon de spécifier une beginDate calée sur cet offset afin d'avoir les données pré-calculées avec un temps de réponse plus rapide.

## [](#api)API

### [](#get-hemis-rest-data)GET hemis/rest/data

*   Permet de faire des requêtes au _DataProvider_ pour récupérer les points d'une ou plusieurs séries temporelles sélectionnées par des filtres (dates, tags, fields).
*   On peut spécifier une _granularité_ (0: temps réel, ou synthèse sur intervalle (en seconde), par ex. gran=3600 --> par heure
*   On peut demander seulement les n premiers ou les n derniers points d'une requête
*   Deux formats de dates : soit les paramètres _begin_ et _end_ sont spécifiés (timestamps en ms) et ils sont pris en compte en priotité ; soit les paramètres _beginDate_ et _endDate_ qui sont de la forme (yyyy-MM-dd) ou (yyyy-MM-ddThh:mm:ss)
*   Un paramètre _aggregator_ permet d'aggréger tous les points d'une série en une seule valeur. (valeurs possibles : COUNT, MEAN, MAX, MIN, ALL et NONE)

**Avertissement :**  
L'utilisation de cette API nécessite une certaine responsabilité dans les appels effectués. Même si les réponses ont une taille limite et qu'une requête trop massive (très long intervalle de temps, ou peu de filtrage sur les séries dans le cas d'un Hemis important (beaucoup de zones, beaucoup d'objets, p. ex. en tertiaire)) activera la pagination, il n'en demeure pas moins que de telles requêtes sont quand même très couteuses en ressources. Elles doivent donc être utilisées avec parcimonie, voire évitées. Dans la mesure du possible il faut bien définir les séries désirées grâce aux tags ainsi que les plages de temps grâce aux dates ou au paramètre _last_.

**Exemples de requêtes :**

*   _/hemis/rest/data_ (appel sans paramètres) \[déconseillé - à éviter\] :
    *   Pas de filtrage sur les tags donc on demande toutes les séries sans restrictions.
    *   Le paramètre par défaut de granularité sera utilisé : 0 (temps réel).
    *   Pas de fields : on demande tous les fields disponibles dans chaque série (N.B. comme c'est du temps réel, on aura _VALUENB_ pour les séries quantitatives et _VALUESTR_ pour les autres ; et _RELIABILITY_ dans les deux cas.
    *   Pas de dates : on demande tous les points existants dans chaque série.
    *   Si _last_ n'est pas spécifié, il n'y a pas de limite de nombre de points par série.
*   _/hemis/rest/data?nature=FACT&zone=salon\_1234&granularity=3600&last=12_ :
    *   Les tags _nature_ et _zone_ sont filtrés : on va récupérer toutes les séries de facteurs environnementaux (_FACT_) dans la zone _salon\_1234_.
    *   La granularité est spécifiée : 3600 (une valeur par heure).
    *   Pas de fields : on demande tous les fields disponibles dans chaque série.
    *   Pas de dates : on demande tous les points existants dans chaque série mais ...
    *   ... Le paramètre _last_ est spécifié : on veut les 12 dernières valeurs disponibles. (N.B. cela ne signifie pas les 12 dernières heures, mais les 12 derniers points. En cas de données manquantes, cela peut retourner des données antérieures au 12 heures précédant la demande (pour obtenir les 12 dernières heures, il faudrait utiliser une beginDate égale à _t courant_\-12h)).
*   _/hemis/rest/data?dsid=047B84D2446281&nature=IT&group=C\_STATE&granularity=900&begin=1596232800000&end=1596319200000&fields=LAST_ :
    *   Les tags _dsid_, _nature_ et _group_ sont filtrés : on va récupérer toutes les séries d'IT States' (_IT_ + _C\_STATE_) pour l'objet dont l'itId est _047B84D2446281_
    *   La granularité est spécifiée : 900 (une valeur par 15 min).
    *   On demande le field _LAST_, on aura donc seulement celui-ci (et pas MAXIMUM\_OCC ni RELIABILITY puisque qu'il s'agit d'une série non quantitative). Ici le field LAST nous donnera donc la dernière valeur perçue à chaque quart d'heure.
    *   Entre 2 dates : ici on aura tous les IT States de l'objet à chaque quart d'heure pour la journée du 1er août 2020.
*   _/hemis/rest/data?measurement=TEMP&zone=salon\_1234&granularity=86400&begin=1596232800000&fields=AVERAGE;NBPOINT_ :
    *   Les tags _measurement_ et _zone_ sont filtrés : on va récupérer toutes les séries de la zone _salon\_1234_ qui concerne la notion de température. Donc par exemple : les relevé des capteurs de température, les états des actionneurs (chauffages, clim, ...), les facteurs, la température des vannes, etc.
    *   La granularité est spécifiée : 86400 donc une valeur par jour.
    *   On demande les fields _AVERAGE_ et _NBPOINT_, on aura donc seulement ceux-là (et pas MAXIMUM ni MINIMUM puisque qu'il s'agit d'une série quantitative). Ici _AVERAGE_ donne la moyenne du jour et _NBPOINT_ le nombre de points (de mesure) du jour.
    *   Seule la _beginDate_ est spécifiée : ici on aura tous les points à partir du 1er août 2020.
*   _/hemis/rest/data?nature=FACT&group=CPOW&zone=MyHemis&granularity=3600&fields=DIFF&last=3_ :
    *   Les tags _nature_, _group_ et _zone_ sont filtrés : on va récupérer la série de l'index de consommation électrique du bâtiment.
    *   La granularité est spécifiée : 3600 donc une valeur par heure.
    *   On demande le field _DIFF_, il ne s'agit donc pas de l'index mais de l'écart sur la période synthétisée. Par conséquent on aura l'écart d'index entre chaque heure, donc la consommation de chaque heure. (NB. si on avait voulu la valeur absolu de l'index, on aurait utilisé _MINIMUM_ ou _MAXIMUM_ (ou _VALUENB_ en temps réel)).
    *   Pas de dates : on demande tous les points existants dans chaque série mais ...
    *   ... Le paramètre _last_ est spécifié : on veut les 3 dernières valeurs disponibles, i.e. les trois derniers points par heure disponibles, quelque soient leurs dates.

**Réponse :**

*   _answer_ : le type de réponse
    *   _SUCCESS_ : des points sont retournés et aucun point manquant détecté
    *   _PARTIAL_ : des points sont retournés mais certaines plages de synthèse sur la période demandée n'ont pas de points.
    *   _FAIL_ : aucun point n'est retourné pour cette requete (il n'y a pas de données pour le filtrage demandé)
    *   _ERROR_ : une erreur est survenue (la requête est incorrecte ou problème interne)
*   _query_ : la requête effectuée est retournée. Si il y a pagination (requête trop volumineuse) :
    *   Le field _pagingNewBeginDate_ ou _pagingNewEndDate_ est ajouté à cette requête.
    *   Le cas échéant il faudra remplacer _begDate_ ou _endDate_ par cette date dans la prochaine requête pour obtenir la page suivante.
*   _results_ : cette liste contient toutes les séries de points
*   _missing_ : cette liste contient les intervalles de donnée manquants en cas de réponse _PARTIAL_ (sous forme de requêtes)
*   _firstDate_ : date du point le plus ancien parmis tous les points de la réponse (toutes séries confondues).
*   _lastDate_ : date du point le plus récent parmis tous les points de la réponse (toutes séries confondues).
*   _pointCount_ : nombre total de points retournés dans la réponse (toutes séries confondues).

**Exemple de réponse :**

```
{
    "answer": "SUCCESS",
    "query": {
        "fields": [],
        "measur": "TEMP",
        "group": null,
        "nature": null,
        "custpid": null,
        "dsid": null,
        "zone": "1038521",
        "begdate": null,
        "enddate": null,
        "gran": 0,
        "last": 1,
        "pagingResetBeginDate": null
    },
    "results": [
        ...
    ],
    "missing": [],
    "firstDate": 1599414600461,
    "lastDate": 1599468929650,
    "pointCount": 4
}
```

*   On voit qu'on a demandé tous les derniers points (_last_\=1) en temps réel (_gran_\=0) des séries concernant la température (measur=TEMP) pour la zone _1038521_.
*   La requête est un succès et on a obtenu 4 points (N.B. donc 4 points de 4 séries différentes car puisque _last_\=1 on ne peut avoir qu'un seul point par série).
*   Les séries sont situées dans le champ _results_ détaillé ci-dessous :

```
"results": [
        {
            "dataInfo": {
                "sourceTypeInfo": {
                    "sourceNature": "TAR",
                    "sourceGroup": "TMP",
                    "customPersistenceId": "",
                    "measurement": "TEMP",
                    "measurementUnit": "°C"
                },
                "zoneId": "1038521",
                "sourceId": "TAR_TMP_1038521"
            },
            "data": {
                "header": {
                    "columns_mapping": {
                        "VALUENB": 0,
                        "RELIABILITY": 1
                    }
                },
                "data_points": [
                    {
                        "d": 1599414600461,
                        "v": [
                            32.0,
                            1.0
                        ]
                    }
                ]
            }
        },
        {
            "dataInfo": {
                "sourceTypeInfo": {
                    "sourceNature": "FACT",
                    "sourceGroup": "TMP",
                    "customPersistenceId": "",
                    "measurement": "TEMP",
                    "measurementUnit": "°C"
                },
                "zoneId": "1038521",
                "sourceId": "FACT_TMP_1038521"
            },
            "data": {
                ...
            }
        },
        {
            ...
        },
        {
            ...
        }
    ]
            "data": {
```

*   Une série (objet de la liste _results_) est constituée de :
    *   _dataInfo_ : un descriptif des tags de la série.
    *   _data_ : les données, composées de :
        *   _header_ : décrit l'ordre des _fields_ utilisé dans le champ _data\_points_
        *   _data\_points_ : la liste des points \[date (_d_) + valeurs (_v_) des différents _fields_\]
*   La première série est ici la _TARGET_ dont la dernière valeur est ici égale à 32°C dans cette zone
*   On a également dans cette réponse la série du facteur environnemental _TMP_ et deux autres qui ne sont pas affichées dans cet exemple.

### [](#get-hemis-rest-data-series)GET hemis/rest/data/series

*   Utile pour connaître uniquement l'ensemble des séries (correspondant aux filtres) disponibles dans un bâtiment, sans récupérer de données.
*   On peut filtrer par _measurement_, _nature_, _group_ et _zone_.

**Exemple de requête :**

*   _/hemis/rest/data/series?nature=FACT_ : on obtient toutes les séries de facteurs environnementaux du bâtiment.
*   _/hemis/rest/data/series?zone=1038640_ : on obtient toutes les séries de la zone _1038640_.

**Exemple de réponse :**

```
[
    {
        "measurement": "BTRY_LVL",
        "measurementUnit": "%",
        "series": [
            {
                "nature": "SEN",
                "group": "BATTERY_LEVEL",
                "zone": "1038640",
                "sourceID": "05888444#3_C3",
                "cpid": null
            },
            {
                "nature": "SEN",
                "group": "BATTERY_LEVEL",
                "zone": "1038640",
                "sourceID": "058d722e#3_C3",
                "cpid": null
            }
        ]
    },
    {
        "measurement": "IND_OCC",
        "measurementUnit": "%",
        "series": [
            {
                "nature": "FACT",
                "group": "OCC",
                "zone": "1038640",
                "sourceID": "FACT_OCC_1038640",
                "cpid": null
            }
        ]
    },
    {
        "measurement": "SENSOR_NOTIFICATION",
        "measurementUnit": "NONE",
        "series": [
            {
                "nature": "SEN",
                "group": "MVT",
                "zone": "1038640",
                "sourceID": "058a8375#0_C1",
                "cpid": null
            },
            {
                "nature": "FACT",
                "group": "MVT",
                "zone": "1038640",
                "sourceID": "FACT_MVT_1038640",
                "cpid": null
            }
        ]
    },
    {
        "measurement": "TEMP",
        "measurementUnit": "°C",
        "series": [
            ...
        ]
    },
    {
        "measurement": "ACT_INT",
        "measurementUnit": "%",
        "series": [
            ...
        ]
    }
]
```

*   Les séries sont groupées par _measurement_.
*   On a 2 séries de capteurs de charge de batterie (_measurement_ _BTRY\_LVL_ en %), une pour l'objet _05888444#3\_C3_ et une pour _058d722e#3\_C3_.
*   On a une série pour le facteur de probabilité de présence dans cette zone (_IND\_OCC_ en %)
*   On a 2 séries de détection de mouvement (_measurement_ _SENSOR\_NOTIFICATION_ sans unité (états discrets)) : une pour le facteur _MVT_ (notons que dans le cas d'un facteur le sourceId est composé de _nature\_group\_zone_) et une pour le capteur _058a8375#0\_C1_.
*   Egalement, on a des séries (non affichées dans cet exemple) pour le measurement _TEMP_ en °C et pour le measurement _ACT\_INT_ en % (intensité des actionneurs).

### [](#get-hemis-rest-data-types-data-source-type-id)GET hemis/rest/data/types/_dataSourceType\_ID_

*   Utile pour connaitre la façon dont est persistée une série, et donc les granularités disponibles en base.
*   Dans le cas où les retention policies auraient changé au cours du temps, permet de connaître l'historique de ces changements.
*   Il faut utiliser l'ID du _DataSourceType_. L'id doit être formé comme ceci : _nature\_group\_cpid_.

**Exemple de requête :**

*   _/hemis/rest/data/types/SEN\_TMP_ : retourne la politique de rétention des données issues des capteurs de température.

**Exemple de réponse :**

```
{
    "id": "SEN_TMP",
    "sourceNature": "SEN",
    "sourceGroup": "TMP",
    "customPersistenceId": "",
    "measurement": "TEMP",
    "sourceGroupUnit": "°C",
    "measurementUnit": "°C",
    "persistenceDescriptions": {
        "0": {
            "fields": [
                "VALUENB",
                "RELIABILITY"
            ],
            "persistencePolicies": [
                {
                    "retainDuration": 8035200,
                    "granularity": 0,
                    "ID": "M3rt"
                },
                {
                    "retainDuration": 63072000,
                    "granularity": 3600,
                    "ID": "Y2ph"
                },
                {
                    "retainDuration": 315360000,
                    "granularity": 86400,
                    "ID": "Y10pd"
                }
            ],
            "intervalCountBeforeAggregation": 2,
            "aggregationTimes": 2,
            "isCustom": false
        }
    },
    "active": true
}
```

*   Dans l'objet _persistenceDescriptions_ on a une liste des différents modes de retention au cours du temps, triés par date. Ici on en a un seul, la date 0 qui indique qu'il n'y a jamais eu de changement.
*   Dans _fields_ on trouve les fields de base : ceux qui sont injectés dans le _Dataprovider_ dans la granularité inférieure i.e. non issus des synthèses automatiques.
*   Dans _persistencePolicies_ on trouve les différentes granularité conservées, et le temps qu'elles sont conservées (fenêtres glissantes)
    *   Le temps réel (_granularity_\=0) est conservé 8035200 s (soit 3 mois), le _par heure_ (_granularity_\=3600) est conservé 2 ans et le _par jour_ (_granularity_\=86400) est conservé 10 ans
    *   Notons que l'ID des _retention policies_ permet de l'interpréter facilement : la première lettre suivit d'un chiffre indique la durée (ex. _M3_ : 3 mois) et la deuxième partie indique la granularité (ex : _rt_ : _realtime_)
    *   _Y2ph_ : 2 Years - per hour / _Y10pd_ : 10 Years - per day
*   N.B. Ces granularités sont uniquement celles qui sont stockées. Néanmoins, cela ne veut pas dire que l'on ne peut pas demander d'autres granularités intermédiaires. Par exemple, on peut demander une valeur toutes les 30 min (_gran=1800_). La réponse sera automatiquement calculée à partir du temps réel (ou pour une valeur tous les 5 jours : la réponses sera calculée à partir du _per day_) . Il faut simplement être conscient que les requêtes seront plus rapides pour des données déjà précalculées et stockées.

### [](#get-hemis-rest-data-types)GET hemis/rest/data/types

*   Permet de récupérer l'ontologie, c'est-à-dire l'ensemble des _DataSourceType_ avec leur historique des DataPersistenceDescription associés au fil du temps. Un paramètre (_full_) permet de récupérer l'ontologie complète d'hemis (tous les types possibles) ou bien seulement ceux existants dans l'hemis.