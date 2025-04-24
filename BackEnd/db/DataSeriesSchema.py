from sqlalchemy import Table, Column, Integer, String, MetaData, Boolean, ARRAY, create_engine


metadata_obj = MetaData()

class ModelSchema():
    model = Table(
        "modelSchema",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("owner", String(60), ForeignKey=("user.username"), nullable=False),
        Column("seriesArray", ARRAY(String(60)))
        Column("isPublic", Boolean, nullable=False)
    )

engine = create_engine('test')