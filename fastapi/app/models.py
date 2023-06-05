from tortoise import Model, fields
from tortoise.contrib.postgres.fields import ArrayField
from pydantic import BaseModel
from pydantic.networks import EmailStr
from datetime import datetime
from enum import Enum

from tortoise.contrib.pydantic import pydantic_model_creator


class UserRegister(BaseModel):
    # pip install 'pydantic[email]'
    email: EmailStr = None
    pw: str = None


class SnsType(str, Enum):
    email: str = "email"
    facebook: str = "facebook"
    google: str = "google"
    kakao: str = "kakao"


class Token(BaseModel):
    Authorization: str = None


class UserToken(BaseModel):
    id: int
    pw: str = None
    email: str = None
    name: str = None
    phone_number: str = None
    profile_img: str = None
    sns_type: str = None

    class Config:
        orm_mode = True


class User(Model):
    id = fields.UUIDField(pk=True)
    username = fields.CharField(max_length=20, null=False, unique=False)
    email = fields.CharField(max_length=200, null=False, unique=True)
    password = fields.CharField(max_length=100, null=False)
    is_verified = fields.BooleanField(default=False)


class UserProfile(Model):
    id = fields.UUIDField(pk=True)

    login_from = fields.CharEnumField(SnsType, default=SnsType.email)
    login_country = fields.CharField(
        max_length=20, null=False, default="Unspecified", index=True)
    device_name = fields.CharField(
        max_length=50, null=False, default="Unspecified", index=True)
    device_id = fields.CharField(
        max_length=50, null=False, default="Unspecified", index=True)
    logo = fields.CharField(max_length=200, null=False, default="default.jpg")
    play_ticket = fields.IntField(default=0)

    created_at = fields.CharField(
        max_length=100, null=False)
    last_login_time = fields.CharField(
        max_length=100, null=False, default="0")
    login_count = fields.IntField(default="0")
    is_active = fields.BooleanField(default=True)

    owner = fields.ForeignKeyField("models.User", related_name="profile")


class ProductPurchase(Model):
    id = fields.UUIDField(pk=True)
    product_id = fields.CharField(
        max_length=100, null=False, default="0")
    purchase_date = fields.CharField(
        max_length=100, null=False, default="0")
    store_type = fields.CharField(
        max_length=100, null=False, default="0")
    owner = fields.ForeignKeyField(
        "models.User", related_name="product_purchase")


class LevelPurchase(Model):
    id = fields.UUIDField(pk=True)
    level = fields.CharField(
        max_length=20, null=False, default="0")
    purchase_date = fields.CharField(
        max_length=100, null=False, default="0")
    expiration_date = fields.CharField(
        max_length=100, null=False, default="0")
    owner = fields.ForeignKeyField(
        "models.User", related_name="level_purchase")


class StageClear(Model):
    id = fields.UUIDField(pk=True)
    stage = fields.CharField(
        max_length=20, null=False, default="0")
    gain_star = fields.CharField(
        max_length=200, null=False, default="0")
    owner = fields.ForeignKeyField("models.User", related_name="stage_clear")


class PlayData(Model):
    id = fields.UUIDField(pk=True)
    # username = fields.CharField(max_length=20, null=False)
    block_use_count = fields.IntField(default=0)
    card_use_count = fields.IntField(default=0)
    stage_clear_count = fields.IntField(default=0)
    stage_play_count = fields.IntField(default=0)
    owner = fields.ForeignKeyField("models.User", related_name="play_data")


class Achievement(Model):
    id = fields.UUIDField(pk=True)
    achieve_data = fields.TextField(null=True)
    owner = fields.ForeignKeyField("models.User", related_name="achieve")


class ARView(Model):
    id = fields.UUIDField(pk=True)
    level = fields.CharField(max_length=100, null=False, default="0")
    view_data = fields.CharField(max_length=100, null=False, default="0")
    owner = fields.ForeignKeyField("models.User", related_name="ar_view")


# class ARView(Model):
#     id = fields.UUIDField(pk=True)
#     s100 = ArrayField(element_type="text")
#     s101 = ArrayField(element_type="text")
#     s102 = ArrayField(element_type="text")
#     s103 = ArrayField(element_type="text")
#     s104 = ArrayField(element_type="text")
#     s105 = ArrayField(element_type="text")
#     s106 = ArrayField(element_type="text")
#     s107 = ArrayField(element_type="text")
#     s108 = ArrayField(element_type="text")
#     s109 = ArrayField(element_type="text")
#     s110 = ArrayField(element_type="text")
#     s111 = ArrayField(element_type="text")
#     owner = fields.ForeignKeyField("models.User", related_name="ar_view")


pydantic_user = pydantic_model_creator(
    User, name="User", exclude=("is_verified", ))
pydantic_user_in = pydantic_model_creator(
    User, name="UserIn", exclude_readonly=True, exclude=("is_verified", "created_at", ))
pydantic_user_out = pydantic_model_creator(
    User, name="UserOut", exclude=("password", ))


pydantic_user_profile = pydantic_model_creator(
    UserProfile, name="UserProfile", exclude=("is_active", ))
pydantic_user_profile_in = pydantic_model_creator(
    UserProfile, name="UserProfileIn", exclude_readonly=True,  exclude=("logo", "created_at", "is_verified", "last_login_time", "login_count", "is_active",))
pydantic_user_profile_out = pydantic_model_creator(
    UserProfile, name="UserProfileOut", )


pydantic_product_purchase = pydantic_model_creator(
    ProductPurchase, name="ProductPurchase", )
pydantic_product_purchase_in = pydantic_model_creator(
    ProductPurchase, name="ProductPurchaseIn", exclude_readonly=True, exclude=("purchase_date", ))
pydantic_product_purchase_out = pydantic_model_creator(
    ProductPurchase, name="ProductPurchaseOut", )


pydantic_level_purchase = pydantic_model_creator(
    LevelPurchase, name="LevelPurchase", )
pydantic_level_purchase_in = pydantic_model_creator(
    LevelPurchase, name="LevelPurchaseIn", exclude_readonly=True, exclude=("purchase_date", "expiration_date", ))
pydantic_level_purchase_out = pydantic_model_creator(
    LevelPurchase, name="LevelPurchaseOut", )

pydantic_stage_clear = pydantic_model_creator(
    StageClear, name="StageClear", )
pydantic_stage_clear_in = pydantic_model_creator(
    StageClear, name="StageClearIn", exclude_readonly=True)
pydantic_stage_clear_out = pydantic_model_creator(
    StageClear, name="StageClearOut", )

pydantic_play_data = pydantic_model_creator(
    PlayData, name="PlayData", )
pydantic_play_data_in = pydantic_model_creator(
    PlayData, name="PlayDataIn", exclude_readonly=True)
pydantic_play_data_out = pydantic_model_creator(
    PlayData, name="PlayDataOut", )

pydantic_achieve = pydantic_model_creator(
    Achievement, name="Achievement", )
pydantic_achieve_in = pydantic_model_creator(
    Achievement, name="AchievementIn", exclude_readonly=True)
pydantic_achieve_out = pydantic_model_creator(
    Achievement, name="AchievementOut", )

pydantic_ar_view = pydantic_model_creator(
    ARView, name="ARView", )
pydantic_ar_view_in = pydantic_model_creator(
    ARView, name="ARViewIn", exclude_readonly=True)
pydantic_ar_view_out = pydantic_model_creator(
    ARView, name="ARViewOut", )
