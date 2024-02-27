from import_export import resources, fields, widgets
from materials.models import (
    Design,
    Expenditure,
    Finance,
    LabelStorage,
    LabelStorageHistory,
    MaterialStorage,
    MaterialStorageHistory,
    SpareStorage,
)


class MaterialModelResource(resources.ModelResource):
    material = fields.Field(column_name="Homashyo", attribute="material")
    amount = fields.Field(column_name="Miqdori", attribute="amount", widget=widgets.DecimalWidget())
    amount_type = fields.Field(column_name=" ", attribute="get_amount_type_display")
    price = fields.Field(column_name="Narx", attribute="price", widget=widgets.DecimalWidget())
    confirmed_price = fields.Field(
        column_name="Tasdiqlangan narx", attribute="confirmed_price", widget=widgets.DecimalWidget()
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
    amount = fields.Field(column_name="Miqdori", attribute="amount", widget=widgets.DecimalWidget())
    amount_type = fields.Field(column_name=" ", attribute="get_amount_type_display")
    price = fields.Field(column_name="Narx", attribute="price", widget=widgets.DecimalWidget())
    price_type = fields.Field(column_name=" ", attribute="get_price_type_display")
    where = fields.Field(column_name="Qayerga", attribute="get_where_display")

    updated_at = fields.Field(column_name="Oxirgi yangilanish", attribute="updated_at")
    created_at = fields.Field(column_name="Dastlabki qo'shish", attribute="created_at")

    class Meta:
        model = MaterialStorageHistory
        exclude = "id"


class SpareModelResource(resources.ModelResource):
    spare = fields.Field(column_name="Ehtiyot qism", attribute="spare")
    amount = fields.Field(column_name="Miqdori", attribute="amount", widget=widgets.DecimalWidget())
    amount_type = fields.Field(column_name=" ", attribute="get_amount_type_display")
    price = fields.Field(column_name="Narx", attribute="price", widget=widgets.DecimalWidget())
    confirmed_price = fields.Field(
        column_name="Tasdiqlangan narx", attribute="confirmed_price", widget=widgets.DecimalWidget()
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
    amount = fields.Field(column_name="Miqdori", attribute="amount", widget=widgets.DecimalWidget())
    amount_type = fields.Field(column_name=" ", attribute="get_amount_type_display")
    price = fields.Field(column_name="Narx", attribute="price", widget=widgets.DecimalWidget())
    price_type = fields.Field(column_name=" ", attribute="get_price_type_display")
    where = fields.Field(column_name="Qayerga", attribute="get_where_display")

    updated_at = fields.Field(column_name="Oxirgi yangilanish", attribute="updated_at")
    created_at = fields.Field(column_name="Dastlabki qo'shish", attribute="created_at")

    class Meta:
        model = MaterialStorageHistory
        exclude = "id"


class LabelModelResource(resources.ModelResource):
    label = fields.Field(column_name="Etiketika turi", attribute="label")
    amount = fields.Field(column_name="Miqdori", attribute="amount", widget=widgets.DecimalWidget())
    amount_type = fields.Field(column_name=" ", attribute="get_amount_type_display")
    price = fields.Field(column_name="Narx", attribute="price", widget=widgets.DecimalWidget())
    confirmed_price = fields.Field(
        column_name="Tasdiqlangan narx", attribute="confirmed_price", widget=widgets.DecimalWidget()
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
    amount = fields.Field(column_name="Miqdori", attribute="amount", widget=widgets.DecimalWidget())
    amount_type = fields.Field(column_name=" ", attribute="get_amount_type_display")
    price = fields.Field(column_name="Narx", attribute="price", widget=widgets.DecimalWidget())
    price_type = fields.Field(column_name=" ", attribute="get_price_type_display")
    where = fields.Field(column_name="Qayerga", attribute="get_where_display")

    updated_at = fields.Field(column_name="Oxirgi yangilanish", attribute="updated_at")
    created_at = fields.Field(column_name="Dastlabki qo'shish", attribute="created_at")

    class Meta:
        model = LabelStorageHistory
        exclude = "id"



class DesignModelResource(resources.ModelResource):
    name = fields.Field(column_name="Dizayn nomi", attribute="name")
    sex = fields.Field(column_name="Jins", attribute="get_sex_display")
    season = fields.Field(column_name="Mavsum", attribute="get_season_display")
    weight = fields.Field(column_name="Og'irlik", attribute="weight", widget=widgets.DecimalWidget())
    materials = fields.Field(column_name="Homashyo narxi", attribute="materials", widget=widgets.DecimalWidget())
    expense = fields.Field(column_name="Harajatlar", attribute="expense", widget=widgets.DecimalWidget())
    invalid = fields.Field(column_name="Brak", attribute="invalid", widget=widgets.DecimalWidget())
    building = fields.Field(column_name="Bino amortizatsiya", attribute="building", widget=widgets.DecimalWidget())
    machine = fields.Field(column_name="Stanok amortizatsiya", attribute="machine", widget=widgets.DecimalWidget())
    another_percent = fields.Field(column_name="Boshqa", attribute="another_percent", widget=widgets.DecimalWidget())
    
    class Meta:
        model = Design
        exclude = ("id", "amount", "sex", "season", "total", "created_at",)
        
class DesignPriceHistoryModelResource(resources.ModelResource):
    design_name = fields.Field(column_name="Dizayn nomi", attribute="design_name")
    weight = fields.Field(column_name="Og'irlik", attribute="weight")
    exchange = fields.Field(column_name="Kurs narxi", attribute="exchange")
    materials = fields.Field(column_name="Homashyo narxi", attribute="materials")
    expense = fields.Field(column_name="Harajatlar", attribute="expense")
    invalid = fields.Field(column_name="Brak", attribute="invalid")
    building = fields.Field(column_name="Bino amortizatsiya", attribute="building")
    machine = fields.Field(column_name="Stanok amortizatsiya", attribute="machine")
    another_percent = fields.Field(column_name="Boshqa", attribute="another_percent")
    
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
        
        

class FinanceModelResource(resources.ModelResource):
    executor = fields.Field(column_name="Bajaruvchi", attribute="executor")
    comment = fields.Field(column_name="Izoh", attribute="comment")
    cost = fields.Field(column_name="Miqdori", attribute="cost", widget=widgets.DecimalWidget())
    price_type = fields.Field(column_name="Pul birligi", attribute="get_price_type_display")
    type = fields.Field(column_name="Kirim & Chiqim", attribute="get_type_display")
    class Meta:
        model = Finance
        exclude = "id"
        