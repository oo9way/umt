from django.db.models import Q, ExpressionWrapper, F, Sum, DecimalField, IntegerField

from materials.models import MaterialStorage, MaterialType, SpareType, SpareStorage, LabelStorage, LabelType, Design, \
    PreProduction, Product, ProductStock, ProductSalesCard, ProductSales, Finance


def get_material_storage_data():
    """
    - count of types
    - number of materials
    - total prices
    - total confirmed prices
    """
    main_query = MaterialStorage.objects.filter(is_active="active")

    types = MaterialType.objects.count()
    count = int(main_query.aggregate(Sum("amount"))["amount__sum"] or 1) / 1000

    total_price = main_query.annotate(
        total_price=ExpressionWrapper(
            F('amount') * F('price'),
            output_field=DecimalField(),
        )
    ).aggregate(Sum("total_price"))["total_price__sum"] or 0

    total_confirmed_price = main_query.annotate(
        total_confirmed_price=ExpressionWrapper(
            F('amount') * F('price'),
            output_field=DecimalField(),
        )
    ).aggregate(Sum("total_confirmed_price"))["total_confirmed_price__sum"] or 0

    data = {
        "types_count": types,
        "count": count,
        "total_price": total_price,
        "total_confirmed_price": total_confirmed_price
    }

    return data


def get_spare_storage_data():
    """
    - count of types
    - number of spares
    - total prices
    - total confirmed prices
    """

    main_query = SpareStorage.objects.filter(is_active="active")

    types = SpareType.objects.count()
    count = int(main_query.aggregate(Sum("amount"))["amount__sum"] or 0)

    total_price = main_query.annotate(
        total_price=ExpressionWrapper(
            F('amount') * F('price'),
            output_field=DecimalField(),
        )
    ).aggregate(Sum("total_price"))["total_price__sum"] or 0

    total_confirmed_price = main_query.annotate(
        total_confirmed_price=ExpressionWrapper(
            F('amount') * F('price'),
            output_field=DecimalField(),
        )
    ).aggregate(Sum("total_confirmed_price"))["total_confirmed_price__sum"] or 0

    data = {
        "types_count": types,
        "count": count,
        "total_price": total_price,
        "total_confirmed_price": total_confirmed_price
    }

    return data


def get_label_storage_data():
    """
    - count of types
    - number of labels
    - total prices
    - total confirmed prices
    """

    main_query = LabelStorage.objects.filter(is_active="active")

    types = LabelType.objects.count()
    count = int(main_query.aggregate(Sum("amount"))["amount__sum"] or 0)

    total_price = main_query.annotate(
        total_price=ExpressionWrapper(
            F('amount') * F('price'),
            output_field=DecimalField(),
        )
    ).aggregate(Sum("total_price"))["total_price__sum"] or 0

    total_confirmed_price = main_query.annotate(
        total_confirmed_price=ExpressionWrapper(
            F('amount') * F('price'),
            output_field=DecimalField(),
        )
    ).aggregate(Sum("total_confirmed_price"))["total_confirmed_price__sum"] or 0

    data = {
        "types_count": types,
        "count": count,
        "total_price": total_price,
        "total_confirmed_price": total_confirmed_price
    }

    return data


def get_pre_production_data():
    """
    - count of types
    - number of pre productions
    - total prices
    - total confirmed prices
    """

    main_query = Product.objects.filter(is_active="active")

    types = Design.objects.count()
    count = int(main_query.aggregate(Sum("amount"))["amount__sum"] or 0)

    total_price = main_query.annotate(
        total_price=ExpressionWrapper(
            F('amount') * F('price'),
            output_field=DecimalField(),
        )
    ).aggregate(Sum("total_price"))["total_price__sum"]

    total_confirmed_price = total_price

    data = {
        "types_count": types,
        "count": count,
        "total_price": total_price,
        "total_confirmed_price": total_confirmed_price
    }

    return data


def get_product_data():
    """
    - count of types
    - number of products
    - total prices
    - total confirmed prices
    """

    main_query = ProductStock.objects.filter(is_active="active")

    types = ProductStock.objects.values("design").distinct().count()

    count = main_query.annotate(
        total_amount=ExpressionWrapper(
            F('set_amount') * F('product_per_set'),
            output_field=IntegerField(),
        )
    ).aggregate(Sum('total_amount'))["total_amount__sum"] or 0

    total_price = main_query.annotate(
        total_price=ExpressionWrapper(
            F('set_amount') * F('product_per_set') * F('price'),
            output_field=DecimalField(),
        )
    ).aggregate(Sum("total_price"))["total_price__sum"] or 0

    total_confirmed_price = main_query.annotate(
        total_confirmed_price=ExpressionWrapper(
            F('set_amount') * F('product_per_set') * F('confirmed_price'),
            output_field=DecimalField(),
        )
    ).aggregate(Sum("total_confirmed_price"))["total_confirmed_price__sum"] or 0

    data = {
        "types_count": types,
        "count": count,
        "total_price": total_price,
        "total_confirmed_price": total_confirmed_price
    }

    return data


def get_sales_data():
    """
    - count of clients
    - count of sold products
    - total prices
    - total confirmed prices
    """
    main_query = ProductSales.objects.all()

    types = ProductSalesCard.objects.values("client").distinct().count() or 0

    count = main_query.annotate(
        total_amount=ExpressionWrapper(
            F('amount') * F('per_set'),
            output_field=IntegerField(),
        )
    ).aggregate(Sum('total_amount'))["total_amount__sum"] or 0

    total_price = main_query.aggregate(Sum("cost"))["cost__sum"] or 0

    total_confirmed_price = total_price
    data = {
        "types_count": types,
        "count": count,
        "total_price": total_price,
        "total_confirmed_price": total_confirmed_price
    }

    return data


def get_credits_data():
    """
    - total credits
    - total cash
    - total clients' loans
    - total profit
    """

    main_query = Finance.objects.all()

    total_credits = main_query.filter(type="credit").aggregate(Sum("cost"))["cost__sum"] or 0

    total_debits = ProductSalesCard.objects.all().aggregate(Sum('given_cost'))['given_cost__sum'] or 0

    total_loans = int(ProductSalesCard.objects.all().aggregate(Sum("cost"))["cost__sum"] or 0) - int(total_debits)

    data = {
        "total_credits": total_credits,
        "total_debits": total_debits,
        "total_loans": total_loans,
        "total_profit": get_expected_profit()
    }

    return data


def get_expected_profit():
    sales = ProductSalesCard.objects.all()
    base_costs = 0

    for sale in sales:
        products = sale.productsales_set.all()
        for p in products:
            total_cost = int(p.product.confirmed_price or 0) - int(p.product.price or 0)
            total_amount = int(p.amount or 0) * int(p.per_set or 0)
            base_costs += total_cost * total_amount

    return base_costs
