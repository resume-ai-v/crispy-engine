from api.extensions.db import Base, engine
from api.models.user import User  # Import any other models here too

# This creates all tables defined in models
Base.metadata.create_all(bind=engine)
print("✅ Database initialized.")
