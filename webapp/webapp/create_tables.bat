call env\Scripts\activate

set SQLALCHEMY_DATABASE_URI=mysql+pymysql://dev:devdev@localhost/SnoutScan

python create_tables.py

