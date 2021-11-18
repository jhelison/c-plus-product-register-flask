from __future__ import annotations
from collections import defaultdict
from typing import List, Tuple, Union, Type, TypeVar
import fdb
from decimal import Decimal
from datetime import datetime
from decouple import config

T = TypeVar("T", bound="TrivialClass")


class Singleton(type):
    """Singleton class

    Uses the __call__ to check if the class is already instanciated,
    if not saves the class instance to return when called.
    """

    _instances: dict = {}

    def __call__(cls, *args, **kwargs) -> None:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class FDBHandler(metaclass=Singleton):
    """Main database handler class

    Responsable for making most of the database related functions.
    This class uses the singleton metaclass to main the same database connection across the server.

    Attributes:
        path:
            The database path.
        user:
            The database user.
            Defaults to SYSDBA
        password:
            The database password.
            Defaults to masterkey
    """

    def __init__(
        self, path: str, user: str = "SYSDBA", password: str = "masterkey"
    ) -> None:
        self.con = fdb.connect(path, user, password)

    def fetchall_as_dict(
        self, query: str, params: list = [], one_key: bool = False
    ) -> dict:
        """Fetch all the rows as a vertical or horizontal table

        Attributes:
            query:
                The SQL query.
            params:
                The list of parameters to be passed to the query.
                This atribute is optional
            one_key:
                Organizes the results per column

        Returns:
            A dict the the data fetched
        """

        cur = self.con.cursor()
        cur.execute(query, params)
        coumns_names = [row[0] for row in cur.description]

        data = cur.fetchall()
        cur.close()

        if one_key:
            data_dict = defaultdict(list)
            for row in data:
                for idx in range(len(row)):
                    data_dict[coumns_names[idx]].append(row[idx])
            return dict(data_dict)
        return [
            {coumns_names[idx]: row[idx] for idx in range(len(row))} for row in data
        ]

    def fetchone_as_dict(self, query: str, params: list = []) -> dict:
        """Fetch one rows from the database

        Attributes:
            query:
                The SQL query.
            params:
                The list of parameters to be passed to the query.
                This atribute is optional

        Returns:
            A dict the the data fetched
        """

        cur = self.con.cursor()
        cur.execute(query, params)
        coumns_names = [row[0] for row in cur.description]

        data = cur.fetchone()
        cur.close()

        return {coumns_names[idx]: data[idx] for idx in range(len(data))}

    def execute_query(self, query: str, params: list = []) -> None:
        """Executes a query without returning any data

        This functions is used on querys that don't return any data,
        like updates or creations.

        Attributes:
            query:
                The SQL query.
            params:
                The list of parameters to be passed to the query.
                This atribute is optional
        """

        cur = self.con.cursor()
        cur.execute(query, params)
        cur.close()

    def commit(self) -> None:
        """Commits the work done to databse"""

        self.con.commit()


class FDBModel:
    """Base model for ORM class heritance

    The basic use of this class is to build querys based on class heritance.
    It gets all the atributes used on the classes and build querys based on them,
    returning the objects as classes.

    When setuping the class,
    the __tablename__ must be setted with the table name on the database.
    """

    __tablename__ = None
    __base_limit = 50

    @classmethod
    def all(cls: Type[T], page=None, limit=None) -> List[T]:
        """Return objects for all rows in the table

        Attributes:
            page:
                The page that is going to be fetched.
                This attribute is optional.
            limit:
                The number of rows to be fetched on that page.
                This attribute is optional.

        Returns:
            A list of objects with the data fetched
        """

        query = cls._basic_query(page, limit)

        res = FDBHandler().fetchall_as_dict(query)

        return [cls(**row) for row in res]

    @classmethod
    def find_by_key(cls: Type[T], key_value: Union[str, int]) -> T:
        """Return one object for the finded row. The key value must be provided.

        Attributes:
            key_value:
                The value to build the query uppon, setted as is_primary_key.

        Returns:
            The object found.

        Raises:
            TypeError: When the class don't have any column as is_primary_key.
        """

        primary_key = cls._get_primary_key()

        if not primary_key:
            error = f"Primary key is missing for the class {cls.__class__.__name__}"
            raise TypeError(error)

        query = cls._basic_query()
        query += f" WHERE {primary_key[0]} = ?"

        res = FDBHandler().fetchone_as_dict(query, [key_value])

        return cls(**res)

    @classmethod
    def find_by_columns(
        cls: Type[T], page=None, limit=None, exact: bool = True, **kwargs
    ) -> List[T]:
        """Finds and return objects rows in the table.

        Attributes:
            page:
                The page that is going to be fetched.
                This attribute is optional.
            limit:
                The number of rows to be fetched on that page.
                This attribute is optional.
            exact:
                If true querys the database with exact values,
                if false makes a search by word.
            kwargs:
                Any of the columns passed as attributes on the object class.

        Returns:
            A list of objects with the data fetched.
        """

        if kwargs:
            columns = cls._get_columns()

            wheres = []
            params = []

            for key in kwargs:
                if key in columns:
                    q, p = cls._build_where(kwargs[key], key, exact)
                    wheres.append(q)
                    params += p

            query = cls._basic_query(page, limit)
            query += "WHERE " + " AND ".join(wheres)

            res = FDBHandler().fetchall_as_dict(query, params)
            return [cls(**row) for row in res]
        else:
            return None

    def update(self) -> None:
        """Updates the database with the object.

        It don't commit the database. It must be done by hand.
        """

        if "_on_update" in self.__class__.__dict__:
            self._on_update()

        data = {
            column: self.__dict__[column] for column in self._get_columns()
        }  # Secure way to get the data from the columns using only Columns class

        primary_key = self._get_primary_key()

        if not primary_key:
            error = f"Primary key is missing for the class {self.__class__.__name__}"
            raise TypeError(error)

        for key in primary_key:
            del data[key]

        set_query = [f"{key} = ?" for key in data.keys()]
        params = list(data.values())

        query = """
        UPDATE
            {}
        SET
            {}
        WHERE
            {}
        """.format(
            self.__tablename__,
            ", ".join(set_query),
            " AND ".join([key + " = ?" for key in primary_key]),
        )

        for key in primary_key:
            params.append(self.__dict__[key])

        FDBHandler().execute_query(query, params)

    def insert(self) -> None:
        """Insert a new row to the database.

        It don't commit the database. It must be done by hand.
        """

        if "_on_insert" in self.__class__.__dict__:
            self._on_insert()

        for key, value in list(self._get_next_keys().items()):
            self.__dict__[key] = value

        data = {column: self.__dict__[column] for column in self._get_columns()}

        query = """
        INSERT INTO
            {} ({})
        VALUES
            ({})
        """.format(
            self.__tablename__,
            ", ".join([key for key, value in data.items() if value != None]),
            ", ".join(["?" for _, value in data.items() if value != None]),
        )

        FDBHandler().execute_query(
            query, [value for _, value in data.items() if value != None]
        )

    @classmethod
    def _get_next_keys(cls) -> dict:
        """Find the next available keys for the table based on the is_primary_key.

        It can found the keys based on is_primary_key or use_generator.

        Returns:
            A dict with the columns as key and the next code as value.
        """

        key_columns = cls._get_primary_key()

        res = {}

        for key in key_columns:
            if cls.__dict__[key].use_table_codigo:
                codigo = Codigo.find_by_columns(
                    NOMETABELA=cls.__tablename__, NOMECAMPO=key
                )
                if codigo:
                    codigo = codigo[0]
                    res[key] = str(codigo.ULTIMOCODIGO).rjust(
                        cls.__dict__[key].use_table_codigo, "0"
                    )
                    codigo.ULTIMOCODIGO += 1
                    codigo.update()
                    codigo.commit()

            elif cls.__dict__[key].use_generator:
                query = f"""
                SELECT NEXT VALUE FOR {cls.__dict__[key].use_generator} FROM RDB$DATABASE
                """
                res[key] = FDBHandler.fetchone_as_dict(query)["GEN_ID"]
                cls.commit()

        return res

    @classmethod
    def _basic_query(cls, page: int = None, limit: int = None) -> str:
        """Builds the most basic query.

        Build the most basic query without any filters.

        Attributes:
            page:
                The page that is going to be fetched.
                This attribute is optional.
            limit:
                The number of rows to be fetched on that page.
                This attribute is optional.

        Returns:
            The query as a string.
        """

        return """
        SELECT {}
            {}
        FROM
            {}
        """.format(
            cls._build_pagination_query(page, limit),
            ", ".join([column for column in cls._get_columns()]),
            cls.__tablename__,
        )

    @classmethod
    def _build_pagination_query(cls, page: int, limit: int = None) -> str:
        """Builds the query part responsable for pagination.

        Attributes:
            page:
                The page that is going to be fetched.
                This attribute is optional.
            limit:
                The number of rows to be fetched on that page.
                This attribute is optional.

        Returns:
            The query part as a string.
        """

        if page:
            if page < 1:
                return ""

            if not limit:
                limit = cls.__base_limit
            return f"first {limit} skip {limit * (page - 1)}"
        return ""

    @classmethod
    def _get_primary_key(cls) -> str:
        """Get the columns setted as is_primary_key

        Returns:
            The key as string.
        """

        return [
            key
            for key, value in cls.__dict__.items()
            if isinstance(value, Column) and value.is_primary_key
        ]

    @classmethod
    def _get_columns(cls) -> list:
        """Get all the columns on the class related to the database.

        Returns:
            The list of columns as string.
        """

        return [key for key, value in cls.__dict__.items() if isinstance(value, Column)]

    @staticmethod
    def convert_to_JSON(data: dict) -> str:
        """Convert dict to a array parsing the data.

        Attributes:
            data:
                The data to be converted.

        Returns:
            The data formated as json.
        """

        def data_type_handler(x):
            if isinstance(x, Decimal):
                return float(x)
            elif isinstance(x, datetime):
                return x.strftime("%Y-%m-%d %H:%M:%S")
            return x

        return {key: data_type_handler(value) for key, value in data.items()}

    @staticmethod
    def _build_where(
        value: Union[str, int, float], column: str, exact: bool = True
    ) -> Tuple[str, Tuple[str]]:
        """Build the filter part of the query.

        Attributes:
            value:
                The number or string to be searched on the database.
            column:
                The column that the value will be searched.
            exact:
                If true querys the database with exact values,
                if false makes a search by word.

        Returns:
            The data formated as json.
        """

        query = []
        params = []

        if exact:
            return f"{column} = ?", [value]
        else:
            splited = value.split(" ")
            for word in splited:
                query.append(f"{column} SIMILAR TO '%{word}%'")

            return " AND ".join(query), params

    @staticmethod
    def commit():
        """Commits the work to the database"""

        FDBHandler().commit()

    def __repr__(self) -> str:
        return f"Class {self.__class__.__name__} with {self.__dict__}"


class Column:
    """The base class to represent columns inside the database.

    Attributes:
        is_primary_key:
            Setted if the column is a primary key.
        use_generator:
            Setted if the column uses a generator.
        use_table_codigo:
            Setted if the column is refered on the codigo table
    """

    def __init__(
        self,
        is_primary_key: bool = False,
        use_generator: str = None,
        use_table_codigo: int = None,
    ) -> None:
        self.is_primary_key = is_primary_key
        self.use_generator = use_generator
        self.use_table_codigo = use_table_codigo


class Codigo(FDBModel):
    """Main class for dealing with the CODIGO table.

    This table is used on the C-Plus program.
    It stores some reference codes for some sequencial columns.

    This also can be used as an example on how to apply
    the FDBModel and Columns classes.
    """

    __tablename__ = "CODIGO"

    NOMETABELA = Column(is_primary_key=True)
    NOMECAMPO = Column(is_primary_key=True)
    ULTIMOCODIGO = Column()

    def __init__(self, NOMETABELA, NOMECAMPO, ULTIMOCODIGO):
        self.NOMETABELA = NOMETABELA
        self.NOMECAMPO = NOMECAMPO
        self.ULTIMOCODIGO = ULTIMOCODIGO
