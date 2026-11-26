# L'entreprise et ses données

**ModeShop** (enseigne fictive) vend en ligne des vêtements, chaussures, articles maison,
électronique et beauté. Les données couvrent les commandes du 6 janvier 2025 au 31 janvier 2026.

Temps forts commerciaux : soldes d'été (juin-juillet), **Black Friday (28 novembre 2025)** et
Cyber Monday, Noël (8-22 décembre), soldes d'hiver (janvier).

## Dictionnaire des données

### `data/orders.csv` : une ligne par commande

| Colonne | Description |
|---|---|
| `order_id` | Identifiant unique de la commande |
| `order_date` | Date de l'achat |
| `customer_id` | Identifiant du client |
| `category` | Vêtements, Chaussures, Maison, Électronique, Beauté |
| `amount_eur` | Montant TTC de la commande |
| `status` | `delivered` ou `cancelled` |
| `cancellation_date` | Date d'annulation (vide si livrée) |

### `data/returns.csv` : une ligne par retour

| Colonne | Description |
|---|---|
| `return_id` | Identifiant unique du retour |
| `order_id` | Commande retournée (lien vers `orders.csv`) |
| `return_date` | Date de réception du retour |
| `reason` | Motif déclaré par le client |

## Le stakeholder

**Claire, directrice du service client.** Elle pilote les effectifs du SAV et remonte
les problèmes qualité aux acheteurs. Elle veut une réponse claire, chiffrée, avec une action.
