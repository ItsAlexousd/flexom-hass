# [](#faq)FAQ

La foire aux questions réunit toutes les questions préalablement posées par les utilisateurs. Si une question ne réponds pas à votre demande où si elle n'est pas présente, veuillez contacter par mail [support-dev@ubiant.com](mailto:support-dev@ubiant.com).

- - -

## [](#que-signifie-les-differents-status-des-devices-sur-management)\- Que signifie les différents status des devices sur management ?

**Extrait de la vue de 'management'**

![Image 001 1](/uploads/image-001-1.jpg "Image 001 1")

**Etat des ITs (ancienne version des états) :**

![Arraystates](/uploads/arraystates.png "Arraystates")  
\*[Support Ubiant](https://support.ubiant.com/)  
\*Compte tiers: Netatmo, MyFox, Zepato, Obix  
\*Compte passerelle: Hue, Overkiz

- - -

## [](#que-signifie-les-differents-status-des-devices-sur-lapplication)\- Que signifie les différents status des devices sur l'application ?

**Extrait de la vue de l'application**

Etat des comptes  
![Accounts](/uploads/accounts.jpg "Accounts")  
Mêmes états que management: OK, UNREACHABLE, UNAUTHORIZED, WAITING et RESCUE. Pour l'explication, voir tableau management ci-dessus.

Etats des objets  
![Its](/uploads/its.jpg "Its")

```
"compositeState": {
        "o": "OK",
        "pO": "UNKNOWN",
        "oTs": 1553700745526,
        "pOTs": 1545837937414,
        "oC": "incoming_data",
        "pOC": "default",
        "p": "NOT_NEEDED",
        "pP": "UNKNOWN",
        "pTs": 1553595093111,
        "pPTs": 1545837937414,
        "pC": "added",
        "pPC": "default",
        "r": "OK",
        "pR": "UNKNOWN",
        "rTs": 1553700745526,
        "pRTs": 1545837937414,
        "rC": "incoming_data",
        "pRC": "default"
}

```

SIgnification des états:

*   "o": Operability
*   "pO": PreviousOperability
*   "oTs": OperabilityTimeStamp
*   "pOTs": PreviousOperabilityTimeStamp
*   "oC": OperabilitCause
*   "pOC": PreviousOperabilityCause
*   "p": Pairing
*   "pP": PreviousPairing
*   "pTs": PairingTimeStamp
*   "pPTs": PreviousPairingTimeStamp
*   "pC": PairingCause
*   "pPC": PreviousPairingCause
*   "r": Reachability
*   "pR": PreviousReachability
*   "rTs": ReachabilityTimeStamp
*   "pRTs": PreviousReachbilityTimeStamp
*   "rC": ReachabilityCause
*   "pRC": PreviousReachabiltyCause

Les états peuvent être pour:  
Operabillity\_State: OK, PARTIAL, KO, UNKNOW  
Pairing\_State: OK, IN\_PROGRES, KO, UNKNOW, NOT\_NEEDED  
Reachability\_State: OK, KO, RESCUE, UNKNOW

- - -

## [](#ou-trouver-les-differents-identifiants-des-facteurs-et-leurs-descriptions)\- Où trouver les différents identifiants des facteurs et leurs descriptions ?

La liste des facteurs et leurs descriptions est disponnible à [cette adresse](/custom/factors).

- - -

## [](#pourquoi-quand-je-souhaite-midentifier-sur-hemisphere-https-hemisphere-users-signin-je-recois-une-erreur-de-type-401-unauthorized)\- Pourquoi quand je souhaite m'identifier sur Hemisphère (https://{hemisphere}/users/signin) je reçois une erreur de type '401 Unauthorized' ?

Dans ce cas, il faut vérifier que:

*   Vous possèdez un compte.
*   La requête est de type 'Post'.
*   Le body contient les bonnes informations, c'est à dire votre email et votre mot de passe.

```
{
    "email": "email",
    "password": "mot de passe"
}
```

- - -

## [](#pourquoi-quand-je-souhaite-midentifier-sur-hemisphere-https-hemisphere-users-signin-je-recois-une-erreur-de-type-415-unsupported-media-type)\- Pourquoi quand je souhaite m'identifier sur Hemisphère (https://{hemisphere}/users/signin) je reçois une erreur de type '415 Unsupported Media Type' ?

Dans ce cas, il faut vérifier que:

*   Le Content-Type "application/json" soit bien mentionné dans le Header
*   Le Content-Type "application/json" soit bien mentionné dans le body

- - -

## [](#pourquoi-quand-je-souhaite-midentifier-sur-hemisphere-https-hemisphere-users-signin-je-recois-une-erreur-de-type-could-not-get-any-response)\- Pourquoi quand je souhaite m'identifier sur Hemisphère (https://{hemisphere}/users/signin) je reçois une erreur de type 'Could not get any response' ?

Dans ce cas, il faut vérifier que:

*   L'url de la requête contient bien le **s** de http(**s**)
*   L'url est bien "https://{hemisphere}/users/signin" avec la valeur d'hemisphere
*   Internet soit actif

- - -

## [](#pourquoi-quand-je-souhaite-recuperer-les-informations-de-mes-logements-sur-hemisphere-https-hemisphere-buildings-mine-infos-je-recois-une-erreur-de-type-405-method-not-allowed)\- Pourquoi quand je souhaite récupérer les informations de mes logements sur Hemisphère (https://{hemisphere}/buildings/mine/infos) je reçois une erreur de type '405 Method Not Allowed' ?

Dans ce cas, il faut vérifier que:

*   Une requête de type Get est effectuée.

- - -

## [](#pourquoi-quand-je-souhaite-midentifier-sur-mon-hemis-hemis-base-url-ws-user-management-login-je-recois-une-erreur-de-type-401-unauthorized)\- Pourquoi quand je souhaite m'identifier sur mon Hemis (<hemis\_base\_url>/WS\_UserManagement/login), je reçois une erreur de type '401 Unauthorized' ?

```
{
    "message": "You must loggin to access this service.",
    "cause": null,
    "errors": null,
    "error_id": "UNAUTHORIZED",
    "target": null
}
```

Dans ce cas, il faut vérifier que:

*   L'**authorization\_token** n'ait pas expiré

- - -

## [](#pourquoi-quand-je-souhaite-midentifier-sur-mon-hemis-hemis-base-url-ws-user-management-login-je-recois-une-erreur-de-type-415-unsupported-media-type)\- Pourquoi quand je souhaite m'identifier sur mon Hemis (<hemis\_base\_url>/WS\_UserManagement/login), je reçois une erreur de type '415 Unsupported Media Type' ?

```
{
    "message": "RESTEASY003065: Cannot consume content type",
    "cause": null,
    "errors": null,
    "error_id": "UNSUPPORTED_MEDIA_TYPE",
    "target": null
}
```

Dans ce cas, il faut vérifier que:

*   "x-www-form-urlencoded" est bien le type du body