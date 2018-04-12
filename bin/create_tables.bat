call ..\env\Scripts\activate

rem set SQLALCHEMY_DATABASE_URI=mysql+pymysql://dev:devdev@localhost/SnoutScan
set SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:Pbn6u8Ew1xAiCJh7@localhost:3307/snoutscan

python create_tables.py
