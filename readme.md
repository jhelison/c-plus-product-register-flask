<h3 align="center">
	C-Plus Product Register
</h3>
<p align="center">
	A backend project for React Native C-Plus product register helper
</p>
<div align="center">
	<img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=darkgreen" />
    <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
</div>

# TOC

-   [Description](#description)
    -   [Characteristics](#characteristics)
    -   [How to run](#how-to-run)
    -   [Endpoints](#endpoints)
        -   [/products](#-products)
        -   [/stock](#-stock)
-   [Problems](#problems)
-   [Bugs found](#bugs-found)

# Description

A firebird database helper to register products on a C-plus system.

## Characteristics

-   Uses a firebird ORM build build by me
-   Makes requests on a firebird server
-   Acess the product, price and stock tables to make modifications

## How to run

To start using the server, install it with `poetry install` to add all the dependences.
Change the database path on `.env` to your database path.
And them run the server with the `src/App.py`.

## Endpoints

It have two basic endpoints `/products` and `/stock`

### /products

```http
  GET /products?NOMEPROD={product name}
```

The NOMEPROD uses a non exact search of the item.

Returns the list of products in the database as a array:

```json
[
  {
    "CODPROD": string,
    "CODIGO": string,
    "NOMEPROD": string,
    "UNIDADE": string,
    "DESCMAXIMO": float,
    "FLAGINATIVO": boolean,
    "ESTOQUE": {
      "CODEMPRESA": integer,
      "CODPROD": string,
      "CODSETORESTOQUE": string,
      "ESTATU": float,
      "LAST_CHANGE": string
    },
    "PRECO": float
  }
]
```

### /stock

```http
  GET /stock?CODPROD={product code}
```

Return the stock for the specified product.

```json
{
  "CODEMPRESA": integer,
  "CODPROD": string,
  "CODSETORESTOQUE": string,
  "ESTATU": float,
  "LAST_CHANGE": string
}
```

```http
  PATCH /stock?CODPROD={product code}
```

Updates the product stock for the specified product code.
It accepts the new stock as:

```json
{
	"amount": integer
}
```

And returns the stock.

```json
{
  "CODEMPRESA": integer,
  "CODPROD": string,
  "CODSETORESTOQUE": string,
  "ESTATU": float,
  "LAST_CHANGE": string
}
```

# Problems

-   The CODEMPRESA is hardcoded to help with the code.

# Bugs found

-   Found bug where json.dumps passed to Flask return as a parsed string.
-   Found bug where if page is not setted on the all function, limit not work also.
