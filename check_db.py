from app import create_app, db
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    # Get all unique constraints for the 'inventory' table
    constraints = inspector.get_unique_constraints('inventory')
    
    print("\n--- EXISTING UNIQUE CONSTRAINTS ---")
    if not constraints:
        print("No unique constraints found.")
    for cc in constraints:
        print(f"Constraint Name: {cc['name']}")
        print(f"Columns: {cc['column_names']}")
    print("-----------------------------------\n")