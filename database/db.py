import sqlite3


class SQLiteDatabase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def disconnect(self):
        self.connection.close()

    def create_tables(self):
        create_tables_query = '''
            CREATE TABLE IF NOT EXISTS [ArcLogs] (
                [id] INTEGER NOT NULL PRIMARY KEY,
                [date] INTEGER NOT NULL,
                [action] NVARCHAR(250) NOT NULL,
                [result] NVARCHAR(250) NOT NULL
            );

            CREATE TABLE IF NOT EXISTS [DisplayTypes] (
                [id] INTEGER NOT NULL PRIMARY KEY,
                [name] NVARCHAR(50) NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS [Languages] (
                [id] INTEGER NOT NULL PRIMARY KEY,
                [name] NVARCHAR(50) NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS [Marks] (
                [id] INTEGER NOT NULL PRIMARY KEY,
                [num] NVARCHAR(255) NOT NULL,
                [name] NVARCHAR(255) NOT NULL,
                [nameEng] NVARCHAR(255),
                [useEng] BOOLEAN NOT NULL DEFAULT FALSE,
                [nameNat] NVARCHAR(1024)
            );

            CREATE TABLE IF NOT EXISTS [Stops] (
                [id] INTEGER NOT NULL PRIMARY KEY,
                [stopIdInPr] NVARCHAR(50) NOT NULL UNIQUE,
                [name] NVARCHAR(50) NOT NULL,
                [nameEng] NVARCHAR(50),
                [nameNat] NVARCHAR(200),
                [lat] DOUBLE NOT NULL,
                [lng] DOUBLE NOT NULL,
                [userEdited] BOOLEAN NOT NULL DEFAULT FALSE,
                [actualDate] DATE
            );

            CREATE TABLE IF NOT EXISTS [UserLogs] (
                [id] INTEGER NOT NULL PRIMARY KEY,
                [date] INTEGER NOT NULL,
                [action] NVARCHAR(250) NOT NULL,
                [result] NVARCHAR(250) NOT NULL
            );
        '''
        self.cursor.executescript(create_tables_query)
        self.connection.commit()

    def insert_data(self, table_name, **kwargs):
        columns = []
        placeholders = []
        values = []
        for key, value in kwargs.items():
            columns.append(key)
            placeholders.append('?')
            values.append(value)
        insert_query = f"INSERT INTO [{table_name}] ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        self.cursor.execute(insert_query, values)
        self.connection.commit()
