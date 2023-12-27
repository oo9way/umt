from django import template
from materials.models import Design, MaterialStorage, Exchange, LabelStorage

register = template.Library()


@register.filter(name='clear_mul_serio')
def clear_mul_serio(value, arg):
    value = float(value)
    arg = float(arg)
    return round(value * arg / 1000, 5)


@register.filter(name='cp')
def cp(value):
    price = 0

    try:
        design = Design.objects.get(id=value)
        design_labels = design.designlabel_set.all()
        design_fields = design.designfield_set.all()
        design_immutables = design.designimmutable_set.all()

        # Seriolarni narxlarini olish
        for df in design_fields:
            material_type = df.material_type
            materials = MaterialStorage.objects.filter(material__id=material_type.id)
            if len(materials) == 0:
                price +=0
            elif len(materials) > 0:
                material = materials.last()
                price += float(material.price) / 1000 * float(df.amount) / float(design.amount)

        # Serio narxlarini kursga o'zgartirish
        exchange = Exchange.objects.last()
        price = price * float(exchange.usd_currency)

        # Dizaynning etiketikalarini qo'shish
        for l in design_labels:
            print(l)
            if l.price == '0' or l.price == None or l.price == '':
                labels = LabelStorage.objects.filter(label__id=l.label.id)
                if len(labels) == 0:
                    price += 0
                elif len(labels) > 0:
                    price += float(labels.last().confirmed_price)
            else:
                price += float(l.price)

        for di in design_immutables:
            if di.calc_type == 'sum':
                price += float(di.cost)

        percent = 0
        for dp in design_immutables:
            if dp.calc_type == 'percent':
                percent += float(dp.cost)

        price = price / 100 * (100 + percent)


    except:
        pass
    return price


@register.filter(name='cg')
def cg(value):
    amount = 0
    try:
        design = Design.objects.get(id=value)
        design_fields = design.designfield_set.all()

        for d in design_fields:
            amount += float(d.amount) / float(design.amount)
    except:
        pass

    return amount


@register.filter(name='dec_div')
def dec_div(value, arg):
    value = float(value)
    arg = float(arg)
    return round(value / arg, 3)