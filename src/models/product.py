from __future__ import annotations
from datetime import datetime
import sys
from typing import Union

sys.path.insert(0, "./")
from src.ORM.FDB_handler import FDBModel, Column


class ProductModel(FDBModel):
    __tablename__ = "PRODUTO"

    CODPROD = Column(is_primary_key=True)
    CODIGO = Column()
    NOMEPROD = Column()
    UNIDADE = Column()
    DESCMAXIMO = Column()
    FLAGINATIVO = Column()
    FLAGNAOVENDER = Column()
    FLAGCONTROLAESTOQUE = Column()

    def __init__(
        self,
        CODPROD: str,
        CODIGO: str,
        NOMEPROD: str,
        UNIDADE: str,
        DESCMAXIMO: int,
        FLAGINATIVO: Union[str, bool],
        FLAGNAOVENDER: Union[str, bool],
        FLAGCONTROLAESTOQUE: Union[str, bool],
    ) -> None:
        self.CODPROD = CODPROD
        self.CODIGO = CODIGO
        self.NOMEPROD = NOMEPROD
        self.UNIDADE = UNIDADE
        self.DESCMAXIMO = DESCMAXIMO

        self.FLAGINATIVO = self.process_boolean(FLAGINATIVO)
        self.FLAGNAOVENDER = self.process_boolean(FLAGNAOVENDER)
        self.FLAGCONTROLAESTOQUE = self.process_boolean(FLAGCONTROLAESTOQUE)

    def json(self) -> str:
        stock = self.get_stock()
        price = self.get_price()

        return self.convert_to_JSON(
            {
                "CODPROD": self.CODPROD,
                "CODIGO": self.CODIGO,
                "NOMEPROD": self.NOMEPROD,
                "UNIDADE": self.UNIDADE,
                "DESCMAXIMO": self.DESCMAXIMO,
                "FLAGINATIVO": self.FLAGINATIVO,
                "FLAGNAOVENDER": self.FLAGNAOVENDER,
                "FLAGCONTROLAESTOQUE": self.FLAGCONTROLAESTOQUE,
                "PRECO": price.PRECO if price else None,
                "ESTOQUE": stock.json() if stock else None,
            }
        )

    def get_stock(self) -> ProductStock:
        product_stock = ProductStock.find_by_columns(CODPROD=self.CODPROD, CODEMPRESA=1)
        if product_stock:
            return product_stock[0]
        return None

    def get_price(self) -> ProductPrice:
        product_price = ProductPrice.find_by_columns(
            CODPROD=self.CODPROD, CODPRECO="000000001"
        )
        if product_price:
            return product_price[0]
        return None

    @staticmethod
    def process_boolean(tag):
        if isinstance(tag, str):
            return tag == "Y"
        else:
            return "Y" if tag else "N"


class ProductStock(FDBModel):
    __tablename__ = "PRODUTOESTOQUE"

    CODPROD = Column(is_primary_key=True)
    CODEMPRESA = Column(is_primary_key=True)
    CODSETORESTOQUE = Column()
    ESTATU = Column()
    LAST_CHANGE = Column()

    def __init__(
        self, CODPROD, CODEMPRESA, CODSETORESTOQUE, ESTATU, LAST_CHANGE
    ) -> None:
        self.CODEMPRESA = CODEMPRESA
        self.CODPROD = CODPROD
        self.CODSETORESTOQUE = CODSETORESTOQUE
        self.ESTATU = ESTATU
        self.LAST_CHANGE = LAST_CHANGE

    def json(self) -> str:
        return self.convert_to_JSON(
            {
                "CODEMPRESA": self.CODEMPRESA,
                "CODPROD": self.CODPROD,
                "CODSETORESTOQUE": self.CODSETORESTOQUE,
                "ESTATU": self.ESTATU,
                "LAST_CHANGE": self.LAST_CHANGE,
            }
        )

    def update(self) -> None:
        self.LAST_CHANGE = datetime.now()
        return super().update()


class ProductPrice(FDBModel):
    __tablename__ = "PRODUTOPRECO"

    CODPRODUTOPRECO = Column(is_primary_key=True)
    CODPROD = Column()
    CODPRECO = Column()
    PRECO = Column()

    def __init__(self, CODPRODUTOPRECO, CODPROD, CODPRECO, PRECO) -> None:
        self.CODPRODUTOPRECO = CODPRODUTOPRECO
        self.CODPROD = CODPROD
        self.CODPRECO = CODPRECO
        self.PRECO = PRECO
