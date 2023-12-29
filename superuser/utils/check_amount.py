from datetime import datetime
from materials.models import Brak, Design, Exchange, LabelStorage, LabelStorageHistory, MaterialStorage, MaterialStorageHistory, Product, ProductionHistory, ProductionMaterialStorageHistory, Worker, WorkerAccount, WorkerWork
import time
from django.db.models import Sum

def check_amount(fields, number, request):
    last_result = []
    errors = []
    sucess = []
    for product in fields:
        log = ''
        states = []
        try:
            check_worker = Worker.objects.get(id=product['worker_id'])
        except:
            states.append(False)
            errors.append({'field_id': product['field_id'], 'msg': f"Ishchi kiritilmagan"})
            continue

        try:
            check_design = Design.objects.get(id=product['design_id'])
        except:
            states.append(False)
            errors.append(
                {'field_id': product['field_id'], 'msg': f"Dizayn kiritilmagan"})
            continue
        
        current_day = datetime.now()

        try:
            exchange = Exchange.objects.get(day=current_day)
            kurs = float(exchange.usd_currency)
        except:
            kurs = 0

        price = 0


        design = Design.objects.get(id=product['design_id'])
        design_amount = 0


        for design_field in design.designfield_set.all():
            # Bitta dizaynning umumiy grami (og'irligi)
            design_amount += float(design_field.amount) / float(design.amount)

        # 2-sort dona va 2-sort gramm > gramga o'tkaziladi
        second_type = float(product['second_type_per']) * \
            design_amount + float(product['second_type_gr'])

        # 3-sort gramm
        third_type = float(product['third_type'])

        # Umumiy brak mahsulot grammda
        total_brak = second_type + third_type

        field_percent = []

        # Tayyor mahsulotning umumiy miqdori grda
        total_design_amount = design_amount * float(product['amount'])

        # Har bir serioning brak mahsulotdan hissasi
        for d_field in design.designfield_set.all():
            # Serioning hissa foizi
            d_field_percent = float(d_field.amount) / \
                float(design.amount) * 100 / design_amount
            
            design_field_qty = float(
                d_field.amount) / float(design.amount) * float(product['amount'])
            # Serioning hissa miqdori
            d_field_qty = total_brak / 100 * d_field_percent
            total_serio_type = d_field_qty + design_field_qty
            field_percent.append(total_serio_type)

        
        for percent in range(len(field_percent)):
            checking_field = design.designfield_set.all()[percent]
            checking_materials = MaterialStorage.objects.filter(
                material=checking_field.material_type).aggregate(Sum('amount'))['amount__sum']

            if checking_field.amount is not None and checking_materials is not None:
                try:
                    if float(field_percent[percent]) <= float(checking_materials):
                        states.append(True)
                    else:
                        states.append(False)
                        errors.append(
                            {'field_id': product['field_id'], 'msg': f"{design.name} uchun yetarli {checking_field.material_type} mavjud emas"})
                except ValueError:
                    states.append(False)
                    errors.append(
                        {'field_id': product['field_id'], 'msg': f"{design.name} uchun yetarli {checking_field.material_type} mavjud emas"})
            else:
                states.append(False)
                errors.append(
                    {'field_id': product['field_id'], 'msg': f"{design.name} uchun yetarli {checking_field.material_type} mavjud emas"})

        for l in design.designlabel_set.all():
            label = LabelStorage.objects.filter(label__pk=l.label.id, is_active='active').aggregate(Sum('amount'))['amount__sum']
        
            if label:
                if float(label) >= float(product['amount']):
                    states.append(True)
                else:
                    errors.append(
                        {'field_id': product['field_id'], 'msg': f"{design.name} uchun yetarli etiketika({l.label}) mavjud emas"})
                    states.append(False)
            else:
                errors.append(
                    {'field_id': product['field_id'], 'msg': f"{design.name} uchun yetarli etiketika({l.label}) mavjud emas"})
                states.append(False)

        if all(state == True for state in states):
            field_range = 0
            for get_field in design.designfield_set.all():
                mat_price = 0
                materials = MaterialStorage.objects.filter(material=get_field.material_type, is_active='active')
                remaining_amount = float(field_percent[field_range])
                for material in materials:
                    mat_price = float(material.confirmed_price)
                    mats_price = float(material.price)
                    
                    if remaining_amount <= 0:
                        break
                    amount_to_subtract = min(remaining_amount, float(material.amount))
                    material.amount = float(material.amount) - amount_to_subtract
                    material.save()
                    remaining_amount = remaining_amount - amount_to_subtract
                    
                    if float(material.amount) == 0:
                        material.delete()
                        
                    ProductionMaterialStorageHistory.objects.create(
                        executor=request.user,
                        production_material=material.material,
                        action = 'import',
                        amount=f'{remaining_amount / 1000 }',
                        amount_type=material.amount_type,
                        price=mats_price,
                        where='production',
                        price_type='usd'
                        
                    )

                    MaterialStorageHistory.objects.create(
                        executor=request.user,
                        material=material.material,
                        action = 'export',
                        amount=f'{remaining_amount / 1000 }',
                        amount_type=material.amount_type,
                        price=mats_price,
                        where='production',
                        price_type='usd'
                    )


                mat_price /= 1000 
                price += mat_price * float(get_field.amount) / float(design.amount)
                field_range += 1

            price = price * kurs

            for l_item in design.designlabel_set.all():
                lb = LabelStorage.objects.filter(label__pk=l_item.label.id, is_active='active')
                rm_amount = float(product['amount'])
                for lb_item in lb:
                    if rm_amount <=0:
                        break
                    a_to_sub = min(rm_amount, float(lb_item.amount))
                    lb_item.amount = float(lb_item.amount) - a_to_sub
                    lb_item.save()
                    rm_amount = rm_amount - a_to_sub

                    ProductionMaterialStorageHistory.objects.create(
                        executor=request.user,
                        production_label=lb_item.label,
                        action='import',
                        amount=f'{remaining_amount }',
                        amount_type=lb_item.amount_type,
                        price=lb_item.confirmed_price,
                        price_type=lb_item.price_type,
                        where='production',
                    )

                    LabelStorageHistory.objects.create(
                        executor=request.user,
                        label=lb_item.label,
                        action="export",
                        amount=remaining_amount,
                        price=price,
                        price_type=lb_item.price_type,
                        amount_type=lb_item.amount_type,
                        where="production",
                    )


                if l_item.price == '' or l_item.price == 0 or l_item.price == '0' or l_item.price == None:
                    print(l_item)
                    price += float(lb.last().price)
                else:
                    price += float(l_item.price)
            

            private_immuts = 0
            for immuts in design.designimmutable_set.filter(calc_type='sum'):
                private_immuts += float(immuts.cost)
            
            price += private_immuts

            imt_perc = 0
            for immuts_percent in design.designimmutable_set.filter(calc_type='percent'):
                imt_perc += float(immuts_percent.cost)


            price = price / 100 * (100+imt_perc)

            old_product = Product.objects.filter(design_type=design).filter(price=price).filter(is_active='active')

            if len(old_product) > 0:
                old_product = old_product.first()
                old_product.amount = float(
                    old_product.amount) + float(product['amount'])
                old_product.save()
            else:
                Product.objects.create(
                    design_type=design,
                    amount=product['amount'],
                    price=price,
                    comment='comment',
                    is_active='active',
                )

            sucess.append(
                {'field_id': product['field_id'], 'msg': f'{design.name} saqlandi', 'input': 'amount'})

            current_month = datetime.now().month
            current_year = datetime.now().year

            worker_profile=Worker.objects.get(id=product['worker_id'])
            worker = WorkerAccount.objects.filter(worker__id=product['worker_id']).filter(created_at__month=current_month, created_at__year=current_year)
            
            worker_works = WorkerWork.objects.create(
                amount=product['amount'],
                cost=product['cost'],
                comment=''
            )
            
            if len(worker)> 0:
                worker = worker.first()
                
                worker.workerworks_cost = float(worker.workerworks_cost) + float(product['amount']) * float(product['cost'])
                worker.workerworks_history.add(worker_works)
                worker.save()
            else:
                new_worker_account = WorkerAccount.objects.create(
                    worker=worker_profile,
                    workerworks_cost=float(
                        product['amount']) * float(product['cost']),
                )
                new_worker_account.workerworks_history.add(worker_works)
                new_worker_account.save()

            sucess.append(
                {'field_id': product['field_id'], 'msg': f'{worker_profile.name}ga kiritildi', 'input': 'worker'})



            ProductionHistory.objects.create(
                executor=request.user,
                production=design.name,
                action='export',
                amount=product['amount'],
                amount_type='uzs',
                price=price,
                where='yaim',
            )

            if all(state == True for state in states):
                if (float(product['second_type_per']) > 0) or (float(product['second_type_gr'])) > 0:
                    Brak.objects.create(
                        design=design,
                        per_amount=product['second_type_per'],
                        gr_amount=product['second_type_gr'],
                        status='active',
                        sort_type='second',

                    )


                    sucess.append(
                        {'field_id': product['field_id'], 'msg': f'2-sort brak saqlandi', 'input': 'second_type_per'})
                    
                    sucess.append(
                        {'field_id': product['field_id'], 'msg': f'2-sort brak saqlandi', 'input': 'second_type_gr'})


                if float(product['third_type']) > 0:

                    Brak.objects.create(
                        gr_amount=product['third_type'],
                        status='active',
                        sort_type='third',

                    )

                    sucess.append(
                        {'field_id': product['field_id'], 'msg': f'3-sort saqlandi', 'input': 'third_type'})


            sucess.append(
                {'field_id': product['field_id'], 'msg': f'{design.name} yuborildi', 'input': 'all'})

            last_result.append(
                {'sent': True, 'design': design.name, 'msg': 'yuborildi.', 'amount': product['amount']})
        else:
            errors.append(
                {'field_id': product['field_id'], 'msg': f"{design.name} saqlanmadi"})
            last_result.append(
                {'sent': False, 'design': design.name, 'msg': 'yetarli xomashyo yo`q.'})

        log = "----- Hisobot -----\n"
        for lr in last_result:
            if lr['sent'] == True:
                log += f"{lr['design']}dan {lr['amount']}ta {lr['msg']}\n"
            else:
                log += f"{lr['design']} - {lr['msg']}\n"

   
    return {'errors': errors, 'success':sucess}



def insert_worker_stats(fields, request):
    errors = []
    success = []

    for stat in fields:
        states = []
        
        try:
            worker = Worker.objects.get(id=stat['worker_id'])
            states.append(True)
        except:
            states.append(False)
            errors.append(
                {'field_id': stat['field_id'], 'msg': f"Ishchi kiritilmagan"})
            continue

        amount = stat['amount']
        cost = stat['cost']

        if amount is not None and cost is not None:
            try:
                amount = float(amount)
                cost = float(amount)
                states.append(True)
            except:
                states.append(False)
                errors.append({'field_id':stat['field_id'], 'msg':"Ish miqdori yoki Narxi noto'g'ri kiritilgan"})
        else:
            states.append(False)
            errors.append(
                {'field_id': stat['field_id'], 'msg': "Ish miqdori yoki Narxi noto'g'ri kiritilgan"})
            
        if all(state == True for state in states):
            current_month = datetime.now().month
            worker_account = WorkerAccount.objects.filter(worker=worker).filter(created_at__month=current_month)
            worker_work_history = WorkerWork.objects.create(
                amount=amount,
                cost=cost,
                comment=''
            )

            if len(worker_account) > 0:
                worker_account = worker_account.last()
                worker_account.workerworks_history.add(worker_work_history)
                worker_account.workerworks_cost = float(
                    worker_account.workerworks_cost) + amount * cost
                worker_account.save()

            else:
                worker_account = WorkerAccount.objects.create(
                    worker=worker,
                    workerworks_cost = amount * cost
                )
                worker_account.workerworks_history.add(worker_work_history)
                worker_account.save()

            success.append({'field_id':stat['field_id']})
    
    return {'errors':errors, 'success':success}