from sqlalchemy import Table, Column, Integer, String, MetaData

metadata_obj = MetaData()

class UserSchema():
    user = Table(
        "user",
        metadata_obj,
        Column("email", String(60), primary_key=True),
        Column("username", String(50), nullable=False)
    )

if __name__=='main'():
    return user