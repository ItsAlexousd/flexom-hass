# [](#introduction)Introduction

Les API REST permettent de récupérer les données d’un hemis. Cependant, ce mode de fonctionnement n’est pas optimal pour la récupération de données temps réel car il engendre un nombre de requête conséquent et introduit une latence dans la récupération de données lié à l’interval entre deux appels REST.

Pour répondre aux besoins d'accès au données temp réel , chaque Hemis expose une API websocket (STOMP).

# [](#connection-et-authentification)Connection et authentification

Pour la récupération des bâtiments associés à un compte, se référer à ce lien: [S'authentifier](/tutoriels/authentification)

L'url du websocket est disponible dans la réponse de l'API **https://{hemisphere}/buildings/mine/infos** **\[1\]** (cf documentation ci-dessus) dans le champ  
**“hemis\_stomp\_url"**.

Le protocol utilisée pour la communication est [STOMP](https://stomp.github.io/index.html "STOMP") ([librairies et implémentation de STOMP](https://stomp.github.io/implementations.html "librairies")).

L’authentification se fait via le protocol STOMP avec les paramètres suivants:

| champ | valeur |
| --- | --- |
| login | identifiant du building (“buildingId” dans la réponse **\[1\]**) |
| password | le token hemis récupéré lors de l’authentification (le même que pour les appels à l’API REST) |

# [](#topics)Topics

Une fois authentifié, l’accès aux données se fait par l’enregistrement sur des _topics_ qui représente les différents flux de données disponibles.

Chaque Hemis expose deux principaux topics:

| nom du topic | description |
| --- | --- |
| jms.topic.{buildingId}.data | Ce topic permet de recevoir tous les événements relatifs aux données capteur, actionneur et facteur. |
| jms.topic.{buildingId}.management | Ce topic permet de recevoir tous les évènements relatifs aux modifications structurelle du bâtiment : ajout/modification/suppression de zone, objects, etc… |

# [](#format-des-messages)Format des messages

Une fois inscrit à un ou aux deux topics, l’hemis enverra les évènements relatifs en temps réel.  
Les données seront transmises au format json. Chaque message contiendra les champs suivants:

| nom | type | description |
| --- | --- | --- |
| type | string | type de message permettant de connaître les champs supplémentaires présents dans l’objet. |
| timestamp | number | timestamp UTC à la milliseconde |

Exemple de message type

| message type | topic | description |
| --- | --- | --- |
| ACTUATOR\_TARGET\_STATE | data | Etat de consigne d'un actionneur |
| ACTUATOR\_HARDWARE\_STATE | data | Valeur de consigne remontée par l'actionneur |
| ACTUATOR\_CURRENT\_STATE | data | Etat interne de l'agent du point de vue d'hemis |
| SENSOR\_STATE | data | Remontée de valeur de capteur. |
| IT\_STATE | data | Modification de l'état d'un objet. |
| FACTOR\_TARGET\_STATE | data | Consigne pour un facteur d'une zone. |
| FACTOR\_CURRENT\_STATE | data | Remontée d'état d'un facteur |
| OBJECTIVE\_STATE | data | Etat d'exécutabilité d'un objectif |
| DATA\_PROVIDER | data | Remontée de donnée au utilisant le format du data provider |
| ENTITY\_MANAGEMENT | management | Evènement de modification structurelle de l'hemis |

- - -

## [](#messages-de-type-state)Messages de type \*\_STATE

| name | type | valeurs | nullable | description |
| --- | --- | --- | --- | --- |
| timestamp | long |     | non |     |
| type | String | ACTUATOR\_TARGET\_STATE | non |     |
| zoneId | String |     | oui |     |
| factorId | String |     | non |     |
| sensorId | String |     | oui | uniquement pour les SENSOR\_STATE |
| itId | String |     | oui | uniquement pout les IT\_STATE |
| valueType | String |     | non | Identifiant permettant de savoir comment parser la valeur (double, string, etc…) |
| value | ITCompositeState, ActuatorState, LightOrder, String |     | non | Valeur renvoyée par le capteur/actionneur. Dont le type peut être inféré par l’attribut value\_type. |

**exemple 1 :** consigne sur la température (value = ActuatorState)

```
{
   "timestamp":12345,
   "type":"ACTUATOR_TARGET_STATE",
   "zoneId":"MyHemis",
   "factorId":"TMP",
   "valueType":"0",
   "value": {
       "id": "123",
       "itId": "123",
       "actuatorId": "12345#C01",
       "value": 20.0,
       "timestamp": 1234525,
       "progressive": false,
       "colorEnable": false,
       "color": null,
       "hsvColor": null,
       "ctEnable": false,
       "ct": null,
       "minActionValue": 7.0,
       "maxActionValue": 35.0,
       "remote": false,
       "direct": true
    }
}
```

**exemple 2 :** remontée de l’état d’un actionneur température (value = ActuatorState)

```
{
   "timestamp":12345,
   "type":"ACTUATOR_HARDWARE_STATE"	,
   "zoneId":"MyHemis",
   "factorId":"TMP",
   "valueType":"0",
   "value": {
       "id": "123",
       "itId": "123",
       "actuatorId": "12345#C01",
       "value": 21.5,
       "timestamp": 1234525,
       "progressive": false,
       "colorEnable": false,
       "color": null,
       "hsvColor": null,
       "ctEnable": false,
       "ct": null,
       "minActionValue": 7.0,
       "maxActionValue": 35.0,
       "remote": false,
       "direct": true
    }
}
```

**exemple 3 :** état d’un it (value = ITCompositeState)

```
{
   "timestamp":12345,
   "type":"IT_STATE",
   "itId":"itid123456",  
   "value": {
       "o": "OK",
       "pO": "UNKNOWN",
       "oTs": 12345,
       "pOTs": 12345,
       "oC": "UNKNOWN",
       "pOC": "UNKNOWN",
       "p": "OK",
       "pP": "OK",
       "pTs": 12345,
       "pPTs": 12345,
       "pC": "UNKNOWN",
       "pPc": "UNKNOWN",
       "r": "OK",
       "pR": "OK",
       "rTs": 12345,
       "pRTs": 12345,
       "rC": "UNKNOWN",
       "pRC": "100"
    }
}
```

**exemple 4 :** remontée de la température

```
{
   "timestamp":12345,
   "type":"SENSOR_STATE",
   "zoneId":"MyHemis",
   "sensorId":"F023B91000000073#1",
   "factorId":"TMP",
   "itId":"041AA72AAA4A80",
   "valueType":"0",
   "value":"21.0"
}
```

**exemple 5 :** remontée du facteur au niveau de la zone

```
{
   "type":"FACTOR_CURRENT_STATE",
   "timestamp":1529420401946,
   "zoneId":"MyHemis",
   "factorId":"OCC",
   "value":99.7
}
```

**exemple 6 :** état d”un objectif (exécutable ou pas)

```
{
   "type":"OBJECTIVE_STATE",
   "timestamp":1529420401946,
   "objectiveId":"123",
   "zoneId":"MyHemis",
   "value":true
}
```

- - -

## [](#messages-de-type-entity-management)Messages de type ENTITY\_MANAGEMENT

| attribute name | type | valeurs | nullable | description |
| --- | --- | --- | --- | --- |
| timestamp | long |     | non |     |
| type | String | ENTITY\_MANAGEMENT | non |     |
| entityType | String | ZONE, AMBIANCE, IT, AGENDA | non | type de l’entité concernée |
| entityId | String |     | non |     |
| action | String | CREATE, DELETE, UPDATE | non | Action réalisée sur l’entité |

**exemple 1 :** création nouvelle Zone

```
{
   "timestamp":12345,
   "type":"ENTITY_MANAGEMENT",
   "entityType":"ZONE",
   "entityId":"Chambre_01",
   "action":"CREATE"
}
```

**exemple 2 :** suppression d’un IT

```
{
   "timestamp":12345,
   "type":"ENTITY_MANAGEMENT",
   "entityType":"IT",
   "entityId":"123456478#C01",
   "action":"DELETE"
}
```

**exemple 3 :** modification d’une Ambiance

```
{
   "timestamp":12345,
   "type":"ENTITY_MANAGEMENT",
   "entityType":"AMBIANCE",
   "entityId":"ambi012345",
   "action":"UPDATE"
}
```

- - -

## [](#message-de-type-data-provider)Message de type DATA\_PROVIDER

| attribute name | type | valeurs | nullable | description |
| --- | --- | --- | --- | --- |
| timestamp | long |     | non |     |
| type | String | DATA\_PROVIDER | non |     |
| container | **DataContainer\*** |     | non | container de données |

Le type **DataContainer** est un type également utilisé pour transmettre des données via l’API d’HEMIS à partir de la version 1.10. Il est composé des éléments suivants :

*   **dataInfo :** contient des métadonnées :
    *   **sourceTypeInfo :** informations sur le type des données :
        *   **sourceNature :** d’où vient la donnée (SENSOR/ACTUATOR/EXTERNAL/FACTOR/PREDICTION)
        *   **sourceGroup :** ce que la donnée représente (ex : TMP/IPOW/…)
        *   **customPersistenceId :** chaîne de caractères utilisée pour différencier 2 types ayant le même sourceNature et sourceGroup (par défaut, la chaîne est vide)
        *   **measurement :** à quelle grandeur physique la donnée correspond
        *   **measurementUnit :** en quelle unité est la donnée
    *   **zoneId :** identifiant de la zone d’où la donnée provient
    *   **sourceId :** identifiant de la source d’où la donnée provient (ex : sensorId)
*   **data :** contient des données et un header pour faire le mapping (cf. columns\_mapping) :
    *   **header :** un header de la liste de données :
        *   **columns\_mapping :** mapping entre le nom de la colonne et l’indice correspondant dans la liste de valeurs des données
        *   **data\_points :** liste de données :  
            \-**d :** date de la donnée  
            \-**v :** liste de valeurs pour la donnée

**exemple :** remontées de données de température

```
{
  	"timestamp" : 1564478716,
    "type" : "DATA_PROVIDER",
    "container": {
        "dataInfo" : {
            "sourceTypeInfo" : {
                "sourceNature" : "SEN",
                "sourceGroup" : "TMP",
                "customPersistenceId" : "",
                "measurement" : "TEMP",
                "measurementUnit" : "°C"
            },
            "zoneId" : "Zone409004",
            "sourceId" : "0400A5818140A9"
        },
        "data" : {
            "header" : {
                "columns_mapping" : {
                    "RELIABILITY" : 1,
                    "VALUENB" : 0,
                    "NBPOINT" : 2
              	}		
            },
            "data_points" : [ {
                "d" : 1564478714,
                "v" : [ 20, 0.8, 1 ]
                }, {
                "d" : 1564478716,
                "v" : [ 21, 0.81, 1 ]
                } 
            ]
        }
    }
}
```

# [](#connection-en-local)Connection en local

Dans le cas ou le client est sur le même réseau local que l’hemis, il est possible d’y accéder directement sans passer par le cloud.

La procédure d’authentification et la récupération des bâtiments est similaire à celle décrite précédement.  
Lorsque l’hemis accepte des connections locales, un champs **local\_ip** sera présent dans le retour de la réponse **\[1\]**.  
La connection stomp devra être ouverte à l’url **wss://{local\_ip}:443** en spécifiant le header HTTP suivant **Host: {hostname of hemis\_stomp\_url}**

**exemple:**

```
{
    "local_ip":"10.0.0.1",
    "hemis_stomp_url":"wss://somename-stomp.eu-west.ubiant.io:4443"
}
```

| Champ | valeur |
| --- | --- |
| URL de connection | wss://10.0.0.1:443 |
| HTTP header | Host: [somename.eu-west.ubiant.io](http://somename.eu-west.ubiant.io) |

**note:**  
Selon les langages clients utilisés, il pourra être nécessaire de modifier la validation du certificat ssl pour qu’elle vérifie que le certificat retourné correspond au hostname et non à l’ip spécifiée.