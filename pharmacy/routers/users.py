from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
import sqlalchemy.exc
from sqlalchemy import select

from pharmacy.dependencies.auth import AuthenticatedUser, get_authenticated_admin
from pharmacy.security import get_hash, password_matches_hashed
from pharmacy.dependencies.database import Database, AnnotatedUser, AnnotatedCartItem
from pharmacy.database.models.users import User
from pharmacy.dependencies.jwt import create_token
from pharmacy.schemas.tokens import Token
from pharmacy.schemas.users import UserCreate, UserSchema
from pharmacy.schemas.cart_items import CartItemCreate, CartItemSchema
from pharmacy.database.models.cart_items import CartItem
from pharmacy.dependencies.database import get_inventory_or_404

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserSchema)
def create_users(user_data: UserCreate, db: Database,) -> User:
    user_data.password = get_hash(user_data.password)
    user = User(**user_data.model_dump())

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

        return user
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
            detail="user already exists")

@router.get("/", response_model=list[UserSchema], 
    dependencies=[Depends(get_authenticated_admin)])
def get_list_of_users(db: Database) -> list[User]:
    return db.scalars(select(User)).all() 

@router.post("/authenticate", response_model=Token)
def login_for_access_token(db: Database, 
    credentials: OAuth2PasswordRequestForm = Depends()):
    
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="incorrect username or password",)

    user: User | None = db.scalar(select(User).where(
        User.username == credentials.username))
    
    if user is None:
        raise credentials_exception
    
    if not password_matches_hashed(plain=credentials.password, hashed=user.password):
        raise credentials_exception

    data = {"sub": str(user.id)}

    token = create_token(data=data)

    return {"token_type": "bearer", "access_token": token}

@router.get("/current", response_model=UserSchema)
def get_current_user(user: AuthenticatedUser) -> User:
    return user

@router.post("/current/cart_items", response_model=CartItemSchema)
def add_item_to_cart(
    user: AuthenticatedUser, 
    cart_item_data: CartItemCreate, 
    db: Database
    ) -> CartItem:
    get_inventory_or_404(db=db, inventory_id=cart_item_data.inventory_id)
    cart_item = CartItem(**cart_item_data.model_dump(), user_id=user.id)

    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)

    return cart_item

@router.get("/current/cart_items", response_model=list[CartItemSchema])
def get_list_of_cart_items(user: AuthenticatedUser, db: Database) -> list[CartItem]:
    return db.scalars(select(CartItem).where(CartItem.user_id == user.id)).all()

@router.delete("/current/cart_items/{cart_item_id}")
def delete_item_from_cart(
    user: AuthenticatedUser, 
    db: Database, 
    cart_item: AnnotatedCartItem
    ) -> None:
    if cart_item.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
            detail="cart item belongs to another user")
    db.delete(cart_item)
    db.commit()

@router.get("/{user_id}", response_model=UserSchema, 
    dependencies=[Depends(get_authenticated_admin)])

def get_user(user: AnnotatedUser) -> User:
    return user

@router.delete("/{user_id}", dependencies=[Depends(get_authenticated_admin)])
def delete_user(user: AnnotatedUser, db: Database) -> None:
    db.delete(user)
    db.commit()