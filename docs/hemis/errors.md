# [](#reponses-et-type-derreurs)Réponses et type d'erreurs

- - -

## [](#200-ok)200 Ok

Tout s'est bien effectué.

- - -

## [](#204-no-content)204 No Content

Tout s'est bien effectué et il n'y a pas de réponse attendue dans le corps de la réponse.

- - -

## [](#401-unauthorized)401 Unauthorized

Vous n'avez pas ou plus accès à la ressource. Il est peut-être seulement nécessaire de raffraichir son **user-token**.

- - -

## [](#404-not-found)404 Not\_Found

L'objet recherché est introuvable.

- - -

## [](#405-method-not-allowed)405 Method not allowed

La ressource existe, cependant elle n'existe pas sous cette forme. Par exemple il existe une requête de type "Get" pour ce service, mais pas de type "Post".

- - -

## [](#415-unsupported-media-type)415 Unsupported media type

Le type de contenu de la requête n'est pas supporté. Par exemple, une requête de type "Post" avec un body au format Json retournera cette erreur si le service demande un formData.

- - -

## [](#422-unprocessable-entity)422 Unprocessable entity

Le type de contenu est correct contrairement à l'erreur 415 ci-dessus. Cependant il y a une erreur de syntaxe dans la demande.

- - -

## [](#500-internal-error)500 Internal error

Dans ce cas-ci, le problème ne vient probablement pas de votre côté.