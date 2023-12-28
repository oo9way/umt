from import_export import resources, fields, widgets
from materials.models import (
    Design,
    Expenditure,
    LabelStorage,
    LabelStorageHistory,
    MaterialStorage,
    MaterialStorageHistory,
    SpareStorage,
)


class MaterialModelResource(resources.ModelResource):
    material = fields.Field(column_name="Homashyo", attribute="material")
    amount = fields.Field(column_name="Miqdori", attribute="amount")
    amount_type = fields.Field(column_name=" ", attribute="get_amount_type_display")
    price = fields.Field(column_name="Narx", attribute="price")
    confirmed_price = fields.Field(
        column_name="Tasdiqlangan narx", attribute="confirmed_price"
    )
    price_type = fields.Field(column_name=" ", attribute="get_price_type_display")
    is_active = fields.Field(column_name="Holati", attribute="get_is_active_display")
    import_comment = fields.Field(column_name="Izoh", attribute="import_comment")
    updated_at = fields.Field(column_name="Oxirgi yangilanish", attribute="updated_at")
    created_at = fields.Field(column_name="Dastlabki qo'shish", attribute="created_at")

    class Meta:
        model = MaterialStorage
        exclude = "id"


class MaterialHistoryModelResource(resources.ModelResource):
    material = fields.Field(column_name="Homashyo", attribute="material")
    executor = fields.Field(column_name="Bajaruvchi", attribute="executor")
    action = fields.Field(column_name="Operatsiya turi", attribute="get_action_display")
    amount = fields.Field(column_name="Miqdori", attribute="amount")
    amount_type = fields.Field(column_name=" ", attribute="get_amount_type_display")
    price = fields.Field(column_name="Narx", attribute="price")
    price_type = fields.Field(column_name=" ", attribute="get_price_type_display")
    where = fields.Field(column_name="Qayerga", attribute="get_where_display")

    updated_at = fields.Field(column_name="Oxirgi yangilanish", attribute="updated_at")
    created_at = fields.Field(column_name="Dastlabki qo'shish", attribute="created_at")

    class Meta:
        model = MaterialStorageHistory
        exclude = "id"


class SpareModelResource(resources.ModelResource):
    spare = fields.Field(column_name="Ehtiyot qism", attribute="spare")
    amount = fields.Field(column_name="Miqdori", attribute="amount")
    amount_type = fields.Field(column_name=" ", attribute="get_amount_type_display")
    price = fields.Field(column_name="Narx", attribute="price")
    confirmed_price = fields.Field(
        column_name="Tasdiqlangan narx", attribute="confirmed_price"
    )
    price_type = fields.Field(column_name=" ", attribute="get_price_type_display")
    is_active = fields.Field(column_name="Holati", attribute="get_is_active_display")
    import_comment = fields.Field(column_name="Izoh", attribute="import_comment")
    updated_at = fields.Field(column_name="Oxirgi yangilanish", attribute="updated_at")
    created_at = fields.Field(column_name="Dastlabki qo'shish", attribute="created_at")

    class Meta:
        model = SpareStorage
        exclude = "id"


class SpareHistoryModelResource(resources.ModelResource):
    spare = fields.Field(column_name="Ehtiyot qism", attribute="spare")
    executor = fields.Field(column_name="Bajaruvchi", attribute="executor")
    action = fields.Field(column_name="Operatsiya turi", attribute="get_action_display")
    amount = fields.Field(column_name="Miqdori", attribute="amount")
    amount_type = fields.Field(column_name=" ", attribute="get_amount_type_display")
    price = fields.Field(column_name="Narx", attribute="price")
    price_type = fields.Field(column_name=" ", attribute="get_price_type_display")
    where = fields.Field(column_name="Qayerga", attribute="get_where_display")

    updated_at = fields.Field(column_name="Oxirgi yangilanish", attribute="updated_at")
    created_at = fields.Field(column_name="Dastlabki qo'shish", attribute="created_at")

    class Meta:
        model = MaterialStorageHistory
        exclude = "id"


class LabelModelResource(resources.ModelResource):
    label = fields.Field(column_name="Etiketika turi", attribute="label")
    amount = fields.Field(column_name="Miqdori", attribute="amount")
    amount_type = fields.Field(column_name=" ", attribute="get_amount_type_display")
    price = fields.Field(column_name="Narx", attribute="price")
    confirmed_price = fields.Field(
        column_name="Tasdiqlangan narx", attribute="confirmed_price"
    )
    price_type = fields.Field(column_name=" ", attribute="get_price_type_display")
    is_active = fields.Field(column_name="Holati", attribute="get_is_active_display")
    import_comment = fields.Field(column_name="Izoh", attribute="import_comment")
    updated_at = fields.Field(column_name="Oxirgi yangilanish", attribute="updated_at")
    created_at = fields.Field(column_name="Dastlabki qo'shish", attribute="created_at")

    class Meta:
        model = LabelStorage
        exclude = "id"


class LabelHistoryModelResource(resources.ModelResource):
    label = fields.Field(column_name="Etiketika", attribute="label")
    executor = fields.Field(column_name="Bajaruvchi", attribute="executor")
    action = fields.Field(column_name="Operatsiya turi", attribute="get_action_display")
    amount = fields.Field(column_name="Miqdori", attribute="amount")
    amount_type = fields.Field(column_name=" ", attribute="get_amount_type_display")
    price = fields.Field(column_name="Narx", attribute="price")
    price_type = fields.Field(column_name=" ", attribute="get_price_type_display")
    where = fields.Field(column_name="Qayerga", attribute="get_where_display")

    updated_at = fields.Field(column_name="Oxirgi yangilanish", attribute="updated_at")
    created_at = fields.Field(column_name="Dastlabki qo'shish", attribute="created_at")

    class Meta:
        model = LabelStorageHistory
        exclude = "id"



class DesignModelResource(resources.ModelResource):
    name = fields.Field(column_name="Dizayn nomi", attribute="name")
    amount = fields.Field(column_name="Juft soni", attribute="amount")
    sex = fields.Field(column_name="Jins", attribute="get_sex_display")
    season = fields.Field(column_name="Mavsum", attribute="get_season_display")
    created_at = fields.Field(column_name="Dastlabki qo'shish", attribute="created_at")

    class Meta:
        model = Design
        exclude = "id"
        
        
class ExpenditureModelResource(resources.ModelResource):
    executor = fields.Field(column_name="Bajaruvchi", attribute="executor")
    comment = fields.Field(column_name="Izoh", attribute="comment")
    cost = fields.Field(column_name="Miqdori", attribute="cost")
    
    class Meta:
        model = Expenditure
        exclude = "id"
        
