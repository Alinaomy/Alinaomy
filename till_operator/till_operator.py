from random import randint

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.lang import Builder
import mysql.connector
import os
import tempfile
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

import re
from kivy.clock import Clock
import datetime
from admin.admin import Notify

Builder.load_file('till_operator/operators.kv')


class OperatorWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='root',
            database='pos',
            auth_plugin='mysql_native_password'
        )

        self.mycursor = self.mydb.cursor()
        sql = 'SELECT * FROM stocks'
        self.mycursor.execute(sql)
        products = self.mycursor.fetchall()
        self.pname = {}
        self.pcode = {}
        self.cart = {}
        self.qty = []
        self.total = 0.00
        self.notify = Notify()
        self.purchase_total = 0.0

    def logout(self):
        self.parent.parent.current = 'scrn_si'

    def date(self, dobj):
        self.ids.date.text = str(dobj)
        pass

    
    def killswitch(self, dtx):
        self.notify.dismiss()
        self.notify.clear_widgets()

    def print(self):
        preview = self.ids.receipt_preview
        prev = preview.text
        company_name = "PROVENDERIE TROPICALE" + "\nTSIANALOKA-TOLIARA" + "\nTEL:+(261)34-77-496-20"
        merci = "MERCI POUR VOTRE VISITE \n\n\n\n\n"
        l = "**********************************************************************************"
        receiptNo = randint(1, 100000)
        date = datetime.datetime.now()
        finalString = company_name + "\nRecipt No: " + str(receiptNo) + "\nDate: " + str(
            date.strftime("%d/%m/%Y %H:%M:%S")) + "\n\n" + prev + "\n\n" + merci + l

        printdata = finalString.encode('utf-8')

        filename = tempfile.mktemp(".txt")
        with open(filename, 'wb') as outf:
            outf.write(printdata)
            # outf.write('\n')

        os.startfile(filename, 'print')

    def update_purchases(self):
        pcode = self.ids.code_inp.text
        products_container = self.ids.products

        # mycursor = self.mydb.cursor()
        sql = 'SELECT product_code, product_name, product_price FROM stocks WHERE product_code =%s'
        values = [pcode]
        self.mycursor.execute(sql, values)
        codes = self.mycursor.fetchone()
        l = []
        # print(codes)
        if not codes:
            self.notify.add_widget(Label(text='[color=#FF0000][b]Invalid Code[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:

            details = BoxLayout(size_hint_y=None, height=30, pos_hint={'top': 1})
            products_container.add_widget(details)
            # for i in len(codes)+1:
            #     k = list(i)
            #     l.append(k[i])
            #     i += 1
            pqty = str(self.ids.qty_inp.text)
            if pqty == '' or 0:
                pqty = 1
            # tot= int(pqty)*
            code = Label(text=pcode, size_hint_x=.2, color=(.06, .45, .45, 1))
            name = Label(text=str(codes[1]), size_hint_x=.3, color=(.06, .45, .45, 1))
            qty = Label(text=str(pqty), size_hint_x=.1, color=(.06, .45, .45, 1))
            disc = Label(text='0.00', size_hint_x=.1, color=(.06, .45, .45, 1))
            price = Label(text=str(codes[2]), size_hint_x=.1, color=(.06, .45, .45, 1))
            total = Label(text=str(float(codes[2]) * float(pqty)), size_hint_x=.2, color=(.06, .45, .45, 1))
            details.add_widget(code)
            details.add_widget(name)
            details.add_widget(qty)
            details.add_widget(disc)
            details.add_widget(price)
            details.add_widget(total)

            # Update Preview
            pname = name.text

            pprice = float(price.text)

            self.total += pprice * float(pqty)
            self.purchase_total = '`\n\n\n\nTotal\t\t\t\t\t\t' + str(self.total)

            self.ids.cur_product.text = pname
            self.ids.cur_price.text = str(pprice)
            preview = self.ids.receipt_preview
            prev_text = preview.text
            _prev = prev_text.find('`')
            if _prev > 0:
                prev_text = prev_text[:_prev]

            ptarget = -1
            for i, c in enumerate(self.cart):

                # print(c)
                if c == pcode:
                    ptarget = i

            # if already exist

            if ptarget >= 0:

                pqty = str(int(self.qty[ptarget]) + int(pqty))
                self.qty[ptarget] = pqty
                expr = '%s\t\tx\d\t' % (pname)
                rexpr = pname + '\t\tx' + str(pqty) + '\t'
                nu_text = re.sub(expr, rexpr, prev_text)
                preview.text = nu_text + self.purchase_total
                # self.cart[pcode] = pname, pprice, pqty
            # if not exist

            else:

                self.cart[pcode] = pname, pprice, pqty
                print(self.cart)

                self.qty.append(1)
                nu_preview = '\n'.join(
                    [prev_text, pname + '\t\tx' + str(pqty) + '\t\t' + str(pprice), self.purchase_total])
                preview.text = nu_preview

            self.ids.disc_inp.text = '0'
            self.ids.disc_perc_inp.text = '0'
            self.ids.qty_inp.text = str(pqty)
            self.ids.price_inp.text = str(pprice)
            self.ids.vat_inp.text = '15%'
            self.ids.total_inp.text = str(pprice * float(pqty))

    def remove_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()
        crud_code = TextInput(hint_text='Product Code')
        crud_submit = Button(text='Remove', size_hint_x=None, width=100,
                             on_release=lambda x: self.remove_product(crud_code.text))

        target.add_widget(crud_code)
        target.add_widget(crud_submit)

    def remove_product(self, code):
        pcode = self.ids.code_inp.text
        if code == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:

            if code in self.cart.keys():
                pprice = self.cart[code][1]
                pqty = self.cart[code][2]
                pname = self.cart[code]
                self.purchase_total = str(self.total - pprice)
                del self.cart[code]
                # pcode = int(code)
                # del self.cart[pcode]
                sold = self.total - pprice
                print(self.cart)
                preview = self.ids.receipt_preview
                prev_text = preview.text
                expr = '%s\t\tx\d\t\t\d' % (pname)

                rexpr = ""
                nu_text = re.sub(expr, rexpr, prev_text)
                preview.text = nu_text + self.purchase_total

    # sql = 'SELECT product_code FROM stocks WHERE product_code =%s'
    # values = [code]
    # self.mycursor.execute(sql, values)
    # codes = self.mycursor.fetchall()
    # if not codes:
    #     self.notify.add_widget(Label(text='[color=#FF0000][b]Invalid Code[/b][/color]', markup=True))
    #     self.notify.open()
    #     Clock.schedule_once(self.killswitch, 1)
    # else:
    #     content = self.ids.scrn_product_contents
    #     content.clear_widgets()
    #
    #     sql = 'DELETE FROM stocks WHERE product_code=%s'
    #     values = [code]
    #
    #     self.mycursor.execute(sql, values)
    #     self.mydb.commit()

    # prodz = self.get_products()
    # stocktable = DataTable(table=prodz)
    # content.add_widget(stocktable)


class OperatorApp(App):
    def build(self):
        return OperatorWindow()


if __name__ == "__main__":
    oa = OperatorApp()
    oa.run()
