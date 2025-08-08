from sqlmodel import Field, Session, SQLModel, create_engine, select, col, or_, func, desc


engine = create_engine("sqlite:///data.db")


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


class Dialog(SQLModel, table=True):
    index: int | None = Field(default=None, primary_key=True)
    idx: int = Field(unique=True, nullable=False)
    speaker: str | None
    text: str | None
