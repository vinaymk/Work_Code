import pandas as pd
import selenium 

 SECTION 1: FASTAPI
Q1. What are the key features of FastAPI compared to Flask?
Answer:

FastAPI is asynchronous and built on Starlette and Pydantic.

Built-in data validation and serialization using Pydantic.

Automatic OpenAPI (Swagger) and ReDoc documentation.

Much faster performance due to async support and type hints.

Dependency injection system.

Q2. How do you define request and response models in FastAPI?
Answer:
By using Pydantic models.

python
Copy
Edit
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
def create_item(item: Item):
    return {"name": item.name, "price": item.price}
Q3. What is dependency injection in FastAPI?
Answer:
It's a way to declare and manage dependencies like DB sessions, authentication, etc., using the Depends() function.

python
Copy
Edit
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/")
def read_users(db: Session = Depends(get_db)):
    ...
Q4. How would you implement authentication in FastAPI?
Answer:
Using OAuth2PasswordBearer and token-based auth (usually JWT). FastAPI provides a fastapi.security module for common schemes.

🔥 SECTION 2: FLASK
Q5. Compare Flask and FastAPI. When would you choose Flask over FastAPI?
Answer:

Flask is simpler and more mature, great for smaller apps or APIs where async is not required.

FastAPI is better for async-heavy apps, strict type checking, and automatic docs.

Flask has a larger ecosystem and more plugins.

Q6. How do you structure a large Flask app?
Answer:
Use Blueprints to split functionality, and application factory pattern for better configurability and testing.

python
Copy
Edit
def create_app():
    app = Flask(__name__)
    app.register_blueprint(user_blueprint)
    return app
Q7. How do you handle errors in Flask?
Answer:
Using custom error handlers:

python
Copy
Edit
@app.errorhandler(404)
def not_found(e):
    return jsonify(error="Not found"), 404
🔗 SECTION 3: SQLAlchemy
Q8. How do you define a SQLAlchemy model and query data?
Answer:

python
Copy
Edit
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)

# Query
db.query(User).filter(User.name == "John").first()
Q9. What's the difference between Session and engine in SQLAlchemy?
Answer:

engine handles DB connections and SQL execution.

Session manages ORM-level interactions, object tracking, and transactions.

Q10. What’s the difference between commit(), flush(), and rollback()?
Answer:

flush() writes changes to the DB but doesn’t commit.

commit() saves changes permanently.

rollback() undoes uncommitted changes.

Q11. What is lazy loading vs eager loading in SQLAlchemy?
Answer:

Lazy loading fetches related data only when accessed.

Eager loading fetches related data up front (e.g., joinedload()).

python
Copy
Edit
from sqlalchemy.orm import joinedload
session.query(User).options(joinedload(User.orders)).all()
Q12. How do you handle migrations in SQLAlchemy?
Answer:
Using Alembic.

bash
Copy
Edit
alembic init alembic
alembic revision --autogenerate -m "Add new table"
alembic upgrade head
