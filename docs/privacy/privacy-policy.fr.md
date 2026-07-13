# Politique de confidentialité — Sentinel Suisse

**Version :** 2026-07-13  
**Statut :** Projet personnel / pré-production (brouillon à valider juridiquement avant mise en ligne publique)

## 1. Responsable du traitement

Sentinel Suisse (projet personnel)  
Contact confidentialité : privacy@sentinel-suisse.example *(à remplacer avant production)*

## 2. Données personnelles collectées

| Donnée | Finalité |
|--------|----------|
| Adresse e-mail | Compte utilisateur, authentification API, alertes e-mail |
| Adresse de canal (e-mail ou téléphone WhatsApp) | Envoi des alertes sur le canal choisi |
| Critères de recherche enregistrés | Correspondance avec les annonces agrégées |
| Journaux d'alertes (statut, horodatage) | Preuve d'envoi, débogage — **sans contenu du message** |

Les annonces agrégées proviennent de sources tierces publiques ; nous ne stockons pas de données sensibles dans le corps des alertes.

## 3. Base légale (nLPD)

- **Service d'alertes :** exécution du contrat / intérêt légitime, avec consentement explicite (inscription + vérification du canal).
- **Agrégation d'annonces :** données publiques de tiers ; lien vers l'annonce source.

## 4. Durée de conservation

| Donnée | Durée |
|--------|-------|
| Compte et canaux | Jusqu'à suppression du compte |
| Recherches enregistrées | Jusqu'à suppression par l'utilisateur ou du compte |
| `raw_payload` des annonces | 30 jours maximum (tâche de maintenance automatique) |
| Journaux d'alertes | Supprimés en cascade avec le compte |

## 5. Sécurité

- Chiffrement au repos (Fernet) pour l'e-mail et les adresses de canal.
- Mots de passe admin hachés (bcrypt) ; clés API hachées — jamais stockées en clair.
- API interne limitée à `127.0.0.1` en phase de développement.

## 6. Sous-traitants et transferts

Selon configuration : fournisseur SMTP (ex. Mailtrap en dev), WhatsApp Cloud API (Meta), hébergeur base de données. Aucun transfert hors Suisse/EEE n'est prévu sans information préalable.

## 7. Vos droits

Conformément à la nLPD, vous disposez notamment des droits d'**accès**, de **rectification** et d'**effacement**.

**Effacement du compte (droit à l'oubli) :**

```http
DELETE /api/v1/users/me
X-API-Key: <votre clé API>
```

La suppression est **définitive** et entraîne la suppression en cascade des canaux, recherches enregistrées et journaux d'alertes associés.

Pour toute demande : privacy@sentinel-suisse.example

## 8. Modifications

Cette politique peut être mise à jour ; la version et la date figurent en tête du document et via l'API `GET /api/v1/legal/privacy?lang=fr`.
