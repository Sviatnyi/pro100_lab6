from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from typing import List, Optional

app = FastAPI()

# Параметри підключення до бази
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="***************",
    database="opendata"
)

# ======== Pydantic моделі ========
class Role(BaseModel):
    name: str

class RoleOut(Role):
    role_id: int

class Category(BaseModel):
    name: str
    parent_category_id: Optional[int] = None

class CategoryOut(Category):
    category_id: int

# ======== ROLE endpoints ========

@app.get("/roles", response_model=List[RoleOut])
def get_roles():
    cursor = db.cursor()
    cursor.execute("SELECT role_id, name FROM role")
    roles = cursor.fetchall()
    return [{"role_id": r[0], "name": r[1]} for r in roles]

@app.post("/roles", response_model=RoleOut, status_code=201)
def create_role(role: Role):
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO role (name) VALUES (%s)", (role.name,))
        db.commit()
        return {"role_id": cursor.lastrowid, "name": role.name}
    except mysql.connector.IntegrityError:
        raise HTTPException(status_code=400, detail="Role with this name already exists")

@app.put("/roles/{role_id}", response_model=RoleOut)
def update_role(role_id: int, role: Role):
    cursor = db.cursor()
    cursor.execute("UPDATE role SET name = %s WHERE role_id = %s", (role.name, role_id))
    db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"role_id": role_id, "name": role.name}

@app.delete("/roles/{role_id}")
def delete_role(role_id: int):
    cursor = db.cursor()
    cursor.execute("DELETE FROM role WHERE role_id = %s", (role_id,))
    db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted"}

# ======== CATEGORY endpoints ========

@app.get("/categories", response_model=List[CategoryOut])
def get_categories():
    cursor = db.cursor()
    cursor.execute("SELECT category_id, name, parent_category_id FROM category")
    cats = cursor.fetchall()
    return [{"category_id": c[0], "name": c[1], "parent_category_id": c[2]} for c in cats]

@app.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(cat: Category):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO category (name, parent_category_id) VALUES (%s, %s)",
        (cat.name, cat.parent_category_id)
    )
    db.commit()
    return {"category_id": cursor.lastrowid, "name": cat.name, "parent_category_id": cat.parent_category_id}

@app.put("/categories/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, cat: Category):
    cursor = db.cursor()
    cursor.execute(
        "UPDATE category SET name = %s, parent_category_id = %s WHERE category_id = %s",
        (cat.name, cat.parent_category_id, category_id)
    )
    db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"category_id": category_id, "name": cat.name, "parent_category_id": cat.parent_category_id}

@app.delete("/categories/{category_id}")
def delete_category(category_id: int):
    cursor = db.cursor()
    cursor.execute("DELETE FROM category WHERE category_id = %s", (category_id,))
    db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted"}
