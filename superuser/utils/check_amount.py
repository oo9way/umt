from datetime import datetime
from materials.models import (
    Brak,
    Design,
    DesignPriceHistory,
    Exchange,
    LabelStorage,
    LabelStorageHistory,
    MaterialStorage,
    MaterialStorageHistory,
    Product,
    ProductionHistory,
    ProductionMaterialStorageHistory,
    Worker,
    WorkerAccount,
    WorkerWork,
)
import time
from django.db.models import Sum


def check_amount(fields, request):
    last_result = []
    errors = []
    sucess = []
    for product in fields:
        log = ""
        states = []
        try:
            check_worker = Worker.objects.get(id=product["worker_id"])
        except:
            states.append(False)
            errors.append(
                {"field_id": product["field_id"], "msg": f"Ishchi kiritilmagan"}
            )
            continue

        try:
            check_design = Design.objects.get(id=product["design_id"])
        except:
            states.append(False)
            errors.append(
                {"field_id": product["field_id"], "msg": f"Dizayn kiritilmagan"}
            )
            continue

        current_day = datetime.now()

        try:
            exchange = Exchange.objects.get(day=current_day)
            kurs = float(exchange.usd_currency)
        except:
            kurs = 0

        price = 0

        design = Design.objects.get(id=product["design_id"])
        design_amount = 0

        for design_field in design.designfield_set.all():
            # Bitta dizaynning umumiy grami (og'irligi)
            design_amount += float(design_field.amount) / float(design.amount)

        # 2-sort dona va 2-sort gramm > gramga o'tkaziladi
        second_type = float(product["second_type_per"]) * design_amount + float(
            product["second_type_gr"]
        )

        # 3-sort gramm
        third_type = float(product["third_type"])

        # Umumiy brak mahsulot grammda
        total_brak = second_type + third_type

        field_percent = []

        # Tayyor mahsulotning umumiy miqdori grda
        total_design_amount = design_amount * float(product["amount"])

        # Har bir serioning brak mahsulotdan hissasi
        for d_field in design.designfield_set.all():
            # Serioning hissa foizi
            d_field_percent = (
                float(d_field.amount) / float(design.amount) * 100 / design_amount
            )

            design_field_qty = (
                float(d_field.amount) / float(design.amount) * float(product["amount"])
            )
            # Serioning hissa miqdori
            d_field_qty = total_brak / 100 * d_field_percent
            total_serio_type = d_field_qty + design_field_qty
            field_percent.append(total_serio_type)

        print(field_percent)
        for percent in range(len(field_percent)):
            print(percent)
            checking_field = design.designfield_set.all()[percent]
            checking_materials = (
                MaterialStorage.objects.filter(
                    material=checking_field.material_type
                ).aggregate(Sum("amount"))["amount__sum"]
                or 0
            )
            checking_materials *= 1000

            if int(checking_field.amount) != 0:
                if checking_materials is not None:
                    try:
                        if float(field_percent[percent]) <= float(checking_materials):
                            states.append(True)
                        else:
                            states.append(False)
                            errors.append(
                                {
                                    "field_id": product["field_id"],
                                    "msg": f"{design.name} uchun yetarli {checking_field.material_type} mavjud emas",
                                }
                            )
                    except ValueError:
                        states.append(False)
                        errors.append(
                            {
                                "field_id": product["field_id"],
                                "msg": f"{design.name} uchun yetarli {checking_field.material_type} mavjud emas",
                            }
                        )
                else:
                    states.append(False)
                    errors.append(
                        {
                            "field_id": product["field_id"],
                            "msg": f"{design.name} uchun yetarli {checking_field.material_type} mavjud emas",
                        }
                    )

        for l in design.designlabel_set.all():
            label = LabelStorage.objects.filter(
                label__pk=l.label.id, is_active="active"
            ).aggregate(Sum("amount"))["amount__sum"]

            if label:
                if float(label) >= float(product["amount"]):
                    states.append(True)
                else:
                    errors.append(
                        {
                            "field_id": product["field_id"],
                            "msg": f"{design.name} uchun yetarli etiketika({l.label}) mavjud emas",
                        }
                    )
                    states.append(False)
            else:
                errors.append(
                    {
                        "field_id": product["field_id"],
                        "msg": f"{design.name} uchun yetarli etiketika({l.label}) mavjud emas",
                    }
                )
                states.append(False)

        if all(state == True for state in states):
            field_range = 0
            for get_field in design.designfield_set.all():
                mat_price = 0
                materials = MaterialStorage.objects.filter(
                    material=get_field.material_type, is_active="active", amount__gt=0
                )
                remaining_amount = float(field_percent[field_range])
                for material in materials:
                    material_amount = float(material.amount) * 1000
                    mat_price = float(material.confirmed_price)
                    mats_price = float(material.price)

                    if remaining_amount <= 0:
                        break
                    amount_to_subtract = min(remaining_amount, float(material_amount))
                    material.amount = (
                        float(material_amount) - amount_to_subtract
                    ) / 1000
                    material.save()

                    remaining_amount = remaining_amount - amount_to_subtract

                    ProductionMaterialStorageHistory.objects.create(
                        executor=request.user,
                        production_material=material.material,
                        action="import",
                        amount=f"{remaining_amount / 1000 }",
                        amount_type=material.amount_type,
                        price=mats_price,
                        where="production",
                        price_type="usd",
                    )

                    MaterialStorageHistory.objects.create(
                        executor=request.user,
                        material=material.material,
                        action="export",
                        amount=f"{remaining_amount / 1000 }",
                        amount_type=material.amount_type,
                        price=mats_price,
                        where="production",
                        price_type="usd",
                    )

                mat_price /= 1000
                price += mat_price * float(get_field.amount) / float(design.amount)
                field_range += 1

            price = price * kurs

            for l_item in design.designlabel_set.all():
                lb = LabelStorage.objects.filter(
                    label__pk=l_item.label.id, is_active="active"
                )
                rm_amount = float(product["amount"])
                for lb_item in lb:
                    if rm_amount <= 0:
                        break
                    a_to_sub = min(rm_amount, float(lb_item.amount))
                    lb_item.amount = float(lb_item.amount) - a_to_sub
                    lb_item.save()
                    rm_amount = rm_amount - a_to_sub

                    ProductionMaterialStorageHistory.objects.create(
                        executor=request.user,
                        production_label=lb_item.label,
                        action="import",
                        amount=f"{rm_amount }",
                        amount_type=lb_item.amount_type,
                        price=lb_item.confirmed_price,
                        price_type=lb_item.price_type,
                        where="production",
                    )

                    LabelStorageHistory.objects.create(
                        executor=request.user,
                        label=lb_item.label,
                        action="export",
                        amount=a_to_sub,
                        price=price,
                        price_type=lb_item.price_type,
                        amount_type=lb_item.amount_type,
                        where="production",
                    )

                if (
                    l_item.price == ""
                    or l_item.price == 0
                    or l_item.price == "0"
                    or l_item.price == None
                ):
                    price += float(lb.last().price)
                else:
                    price += float(l_item.price)

            private_immuts = 0
            for immuts in design.designimmutable_set.filter(calc_type="sum"):
                private_immuts += float(immuts.cost)

            price += private_immuts

            imt_perc = 0
            for immuts_percent in design.designimmutable_set.filter(
                calc_type="percent"
            ):
                imt_perc += float(immuts_percent.cost)

            price = round(price / 100 * (100 + imt_perc), 5)

            old_product = (
                Product.objects.filter(design_type=design)
                .filter(price=price)
                .filter(is_active="active")
            )

            if len(old_product) > 0:
                old_product = old_product.first()
                old_product.amount = float(old_product.amount) + float(
                    product["amount"]
                )
                old_product.save()
            else:
                Product.objects.create(
                    design_type=design,
                    amount=product["amount"],
                    price=price,
                    comment="comment",
                    is_active="active",
                )

            sucess.append(
                {
                    "field_id": product["field_id"],
                    "msg": f"{design.name} saqlandi",
                    "input": "amount",
                }
            )

            current_month = datetime.now().month
            current_year = datetime.now().year

            worker_profile = Worker.objects.get(id=product["worker_id"])
            print("worker found", worker_profile)

            worker = WorkerAccount.objects.filter(
                worker__id=product["worker_id"]
            ).filter(
                created_at__month=current_month,
                created_at__year=current_year,
                completed=False,
            )
            print("worker account found", len(worker))

            worker_works = WorkerWork.objects.create(
                amount=product["amount"],
                cost=product["cost"],
                comment="Ishlab chiqarish",
            )
            print("Worker works created")

            if len(worker) > 0:
                worker = worker.last()

                worker.workerworks_cost = float(worker.workerworks_cost) + float(
                    product["amount"]
                ) * float(product["cost"])
                worker.workerworks_history.add(worker_works)
                worker.save()
                print("Old account saved")
            else:
                new_worker_account = WorkerAccount.objects.create(
                    worker=worker_profile,
                    workerworks_cost=float(product["amount"]) * float(product["cost"]),
                )
                new_worker_account.workerworks_history.add(worker_works)
                new_worker_account.save()
                print("new account was created")

            sucess.append(
                {
                    "field_id": product["field_id"],
                    "msg": f"{worker_profile.name}ga kiritildi",
                    "input": "worker",
                }
            )

            ProductionHistory.objects.create(
                executor=request.user,
                production=design,
                action="export",
                amount=product["amount"],
                amount_type="uzs",
                price=price,
                where="yaim",
            )

            if all(state == True for state in states):
                if (float(product["second_type_per"]) > 0) or (
                    float(product["second_type_gr"])
                ) > 0:
                    Brak.objects.create(
                        design=design,
                        per_amount=product["second_type_per"],
                        gr_amount=product["second_type_gr"],
                        status="active",
                        sort_type="second",
                    )

                    sucess.append(
                        {
                            "field_id": product["field_id"],
                            "msg": f"2-sort brak saqlandi",
                            "input": "second_type_per",
                        }
                    )

                    sucess.append(
                        {
                            "field_id": product["field_id"],
                            "msg": f"2-sort brak saqlandi",
                            "input": "second_type_gr",
                        }
                    )

                if float(product["third_type"]) > 0:
                    Brak.objects.create(
                        gr_amount=product["third_type"],
                        status="active",
                        sort_type="third",
                    )

                    sucess.append(
                        {
                            "field_id": product["field_id"],
                            "msg": f"3-sort saqlandi",
                            "input": "third_type",
                        }
                    )

            sucess.append(
                {
                    "field_id": product["field_id"],
                    "msg": f"{design.name} yuborildi",
                    "input": "all",
                }
            )

            last_result.append(
                {
                    "sent": True,
                    "design": design.name,
                    "msg": "yuborildi.",
                    "amount": product["amount"],
                }
            )
        else:
            errors.append(
                {"field_id": product["field_id"], "msg": f"{design.name} saqlanmadi"}
            )
            last_result.append(
                {"sent": False, "design": design.name, "msg": "yetarli xomashyo yo`q."}
            )

        log = "----- Hisobot -----\n"
        for lr in last_result:
            if lr["sent"] == True:
                log += f"{lr['design']}dan {lr['amount']}ta {lr['msg']}\n"
            else:
                log += f"{lr['design']} - {lr['msg']}\n"

    return {"errors": errors, "success": sucess}


def insert_worker_stats(fields, request):
    errors = []
    success = []

    for stat in fields:
        print(stat)
        states = []

        try:
            worker = Worker.objects.get(id=stat["worker_id"])
            states.append(True)
        except:
            states.append(False)
            errors.append({"field_id": stat["field_id"], "msg": f"Ishchi kiritilmagan"})
            continue

        amount = stat["amount"]
        cost = stat["cost"]

        if amount is not None and cost is not None:
            try:
                amount = float(amount)
                cost = float(cost)
                states.append(True)
            except:
                states.append(False)
                errors.append(
                    {
                        "field_id": stat["field_id"],
                        "msg": "Ish miqdori yoki Narxi noto'g'ri kiritilgan",
                    }
                )
        else:
            states.append(False)
            errors.append(
                {
                    "field_id": stat["field_id"],
                    "msg": "Ish miqdori yoki Narxi noto'g'ri kiritilgan",
                }
            )

        if all(state == True for state in states):
            current_month = datetime.now().month

            worker_account = WorkerAccount.objects.filter(worker=worker).filter(
                created_at__month=current_month, completed=False
            )

            worker_work_history = WorkerWork.objects.create(
                amount=amount, cost=cost, comment="Donabay ish"
            )

            if len(worker_account) > 0:
                worker_account = worker_account.last()
                worker_account.workerworks_history.add(worker_work_history)
                worker_account.workerworks_cost = (
                    float(worker_account.workerworks_cost) + amount * cost
                )
                worker_account.save()

            else:
                worker_account = WorkerAccount.objects.create(
                    worker=worker, workerworks_cost=amount * cost
                )
                worker_account.workerworks_history.add(worker_work_history)
                worker_account.save()

            success.append({"field_id": stat["field_id"]})

    return {"errors": errors, "success": success}


def create_price(design):
    fields = design.designfield_set.all()
    labels = design.designlabel_set.all()
    immutable_prices = design.designimmutable_set.all()

    exchange = Exchange.objects.last()

    material_price = 0
    material_weight = 0

    # Calculate material weight and price of design fields
    for field in fields:
        material_type = field.material_type
        storage = MaterialStorage.objects.filter(material=material_type).last()

        if storage:
            m_price_for_gr = float(storage.price) / 1000
            field_amount = float(field.amount) / float(design.amount)
            field_price = m_price_for_gr * field_amount

            print("Field price", field_price)

            material_price += field_price

        material_weight += float(field.amount) / float(design.amount)

    material_price = round(material_price * float(exchange.usd_currency), 5)

    # Calculate labels of design
    label_price = 0

    for label in labels:
        label_type = label.label

        if label.price != "":
            label_price += float(label.price)

        else:
            storage = LabelStorage.objects.filter(label_type=label_type).last()
            label_price += float(storage.price)

    label_price = round(label_price, 2)

    immutable_price = label_price
    immutable_percent = 0

    building_amortization = 0
    machine_amortization = 0
    invalid = 0

    for immutable in immutable_prices:
        if immutable.calc_type == "sum":
            immutable_price += float(immutable.cost)

        if (
            immutable.calc_type == "percent"
            and immutable.task != "stanok"
            and immutable.task != "building"
            and immutable.task != "brak"
        ):
            immutable_percent += float(immutable.cost)

        if immutable.calc_type == "percent" and immutable.task == "stanok":
            machine_amortization += float(immutable.cost)

        if immutable.calc_type == "percent" and immutable.task == "building":
            building_amortization += float(immutable.cost)

        if immutable.calc_type == "percent" and immutable.task == "brak":
            invalid += float(immutable.cost)

    base_total = material_price + immutable_price

    total_percent = (
        building_amortization + machine_amortization + invalid + immutable_percent
    )
    total_price = round(base_total / 100 * (total_percent + 100), 2)

    building_amortization = round(base_total / 100 * building_amortization, 5)
    machine_amortization = round(base_total / 100 * machine_amortization, 5)
    invalid = round(base_total / 100 * invalid, 5)
    immutable_percent = round(base_total / 100 * immutable_percent, 5)

    DesignPriceHistory.objects.create(
        design_name=design.name,
        exchange=exchange.usd_currency,
        weight=material_weight,
        labels=label_price,
        expense=immutable_price,
        building=building_amortization,
        machine=machine_amortization,
        invalid=invalid,
        another_percent=immutable_percent,
        total=total_price,
    )

    design.weight = material_weight
    design.labels = label_price
    design.expense = immutable_price
    design.building = building_amortization
    design.machine = machine_amortization
    design.invalid = invalid
    design.another_percent = immutable_percent
    design.total = total_price

    design.save()
