[](#bienvenue-dans-la-partie-tutoriel)Bienvenue dans la partie tutoriel
=======================================================================

* * *

La partie tutoriel est composée d'une étape d'authentification sur son bâtiment ainsi qu'un exemple d'utilisation des APIs d'Hemis pour récupérer ou injecter une donnée afin de vous familiariser avec l'utilisation de la documentation de Hemis et de Hemisphere.

Une [faq](/faq) ainsi qu'une [liste des messages d'erreurs et leurs résolutions](/errors-type) peuvent vous aider pendant l'avancement du tutoriel.

* * *

[](#sauthentifier)S'authentifier
--------------------------------

La partie authentification permet de récupérer un "token" par le biais des APIs Hemisphere ainsi que l'identifiant d'un bâtiment pour y accèder puis utiliser les APIs Hemis.

[S'authentifier](/tutoriels/authentification)

* * *

[](#recuperer-une-donnee)Récupérer une donnée
---------------------------------------------

Une fois authentifié, la partie récupèrer une donnée va vous permettre de lire une donnée de l'un de vos objets connectés.

[Récupérer une donnée](/tutoriels/get-data)

* * *

[](#injecter-une-donnee)Injecter une donnée
-------------------------------------------

Une fois authentifié, la partie injecter une donnée va vous permettre d'injecter une donnée dans l'un de vos objets connectés.

[Injecter une donnée](/tutoriels/set-data)



[](#authentification-sur-un-hemis)Authentification sur un Hemis
===============================================================

* * *

L’architecture serveur Hemis est une architecture décentralisée. Les bâtiments sont gérés par des processus séparés répartis sur différents serveurs. Afin de se connecter sur un bâtiment il faut donc se connecter en premier sur Hemisphere. Hemisphere est un serveur qui recense les utilisateurs, les bâtiments et permet de récupérer les informations nécessaires à la connexion sur un Hemis (bâtiment).

[](#login-sur-hemisphere)Login sur Hemisphere
---------------------------------------------

* * *

La première étape consiste à s'identifier sur Hemisphere afin de récupérer le **user\_token** d'identification.

### [](#post)POST

    https://hemisphere.ubiant.com/users/signin
    

### [](#header)Header

    Content-Type: application/json
    

### [](#body)Body

    {
        "email": "email",
        "password": "mot de passe"
    }
    

En remplacant les champs par son email et son mot de passe.

### [](#reponse)Réponse

`200 Authorized`

    {
        "token": "token",
    }
    

[](#recuperation-dun-hemis)Récupération d'un Hemis
--------------------------------------------------

* * *

Le **token** récupéré via l’appel webservice de l'étape précédente permet de récupérer la liste des bâtiments disponnibles, en le placant dans le header de la requête.  
Cette deuxième étape consiste à récupérer l'identifiant d'un Hemis, c'est à dire son **buildingId**.

### [](#get)GET

    https://hemisphere.ubiant.com/buildings/mine/infos
    

### [](#header-2)Header

    Authorization: Bearer <token>
    

### [](#reponse-2)Réponse

`200 OK`

    [
        {
        	"buildingId": "id",
        }
    ]
    

[](#formation-de-lurl-dacces-aux-ap-is-dun-hemis)Formation de l'url d'accès aux APIs d'un hemis
-----------------------------------------------------------------------------------------------

* * *

Pour utiliser les APIs d'hemis, il faut former son **hemis\_base\_url** à l'aide de son **buildingId** récupéré préalablement.

### [](#exemple)Exemple:

    https://{buildingId}.eu-west.hemis.io/hemis/rest/
    

Vous avez de quoi accèder aux APIs d'hemis. Vous pouvez tester de [récupérer une donnée](/tutoriels/get-data)



[](#tutoriels)Récupérer une donnée
=======================

* * *

Récupartion des capteurs ou des actionneurs du bâtiment.

Il est possible d'identifier l'objet à l'aide de l'**itId** et de savoir sur quel capteur ou actionneur on souhaite récupérer la donnée avec l'identifiant du state qui est le facteur environnemental de celui-ci. Dans l'exemple nous récupérons la température (TMP) d'un objet possèdant un capteur ou un actionneur de température. La liste des facteurs est disponnibles [ici](/factors).

[](#recuperer-les-capteurs)Récupérer les capteurs
-------------------------------------------------

* * *

Récupération des capteurs.

### [](#get)GET

    <hemis_base_url>/intelligent-things/sensors
    

### [](#headers)Headers

    Authorization: Bearer <token>
    

    Building-Id: <buildingId>
    

### [](#reponse)Réponse

`200 Authorized`

    [
        {
            "id": "id",
            "itId": "itId",
            "state": {
                "id": "TMP",
                "value": 22.4
            }
        }
    ]
    

[](#recuperer-les-actionneurs)Récupérer les actionneurs
-------------------------------------------------------

* * *

Récupération des capteurs.

### [](#get-2)GET

    <hemis_base_url>/intelligent-things/actuators
    

### [](#headers-2)Headers

    Authorization: Bearer <token>
    

    Building-Id: <buildingId>
    

### [](#reponse-2)Réponse

`200 Authorized`

    [
        {
            "id": "id",
            "itId": "itId",
            "state": {
                "id": "TMP",
                "value": 22.4
            }
        }
    ]



[](#tutoriels)Injecter une donnée
=======================

* * *

Injecter des valeurs dans les actionneurs du bâtiment.

Il est possible d'identifier l'objet à l'aide de l'**itId** et de savoir sur quel actionneur on souhaite agir avec l'identifiant du state qui est le facteur environnemental de celui-ci. On récupère alors l'identifiant de l'actionneur (id) comme vue dans la partie précèdente de récupération de données.

[](#injecter-une-donnee-dans-un-actionneur)Injecter une donnée dans un actionneur
---------------------------------------------------------------------------------

* * *

Injection dans un actionneur. La valeur (value) voulue accompagné d'une durée d'action avec l'attribut "duration" (en millisecondes) qui permet de définir la durée du forçage avant que le système repasse en mode automatique lorsque la régulation est activée doit en défini au format json dans le corps de la requête.

### [](#put)PUT

    <hemis_base_url>/intelligent-things/{itId}/actuator/{actuatorId}/state
    

### [](#headers)Headers

    Authorization: Bearer <token>
    

    Building-Id: <buildingId>
    

### [](#body)Body

       {
          "value": 22.4,
                "duration": 30000
       }
    

### [](#reponse)Réponse

`200 Authorized`