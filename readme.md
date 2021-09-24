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

## Bugs found

-   Found bug where json.dumps passed to Flask return as a parsed string
-   Found bug where if page is not setted on the all function, limit not work also
