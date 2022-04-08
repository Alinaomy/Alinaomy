from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.uix.modalview import ModalView
from kivy.lang import Builder

from collections import OrderedDict
import mysql.connector
from utils.datatable import DataTable
from datetime import datetime
import hashlib



Builder.load_file('admin/admin.kv')


class Notify(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size_hint = (.7, .7)


class AdminWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='root',
            database='pos'
        )

        self.mycursor = self.mydb.cursor()
        sql = 'SELECT * FROM stocks'
        self.mycursor.execute(sql)
        products = self.mycursor.fetchall()

        # sql2 = 'SELECT * FROM users'
        # mycursor.execute(sql2)
        # users = mycursor.fetchall()

        self.notify = Notify()

        product_code = []
        product_name = []
        spinvals = []
        for product in products:
            product_code.append(product[1])
            name = str(product[2])
            if len(name) > 30:
                name = name[:30] + '...'
            product_name.append(name)

        for x in range(len(product_code)):
            line = ' | '.join([product_code[x], product_name[x]])
            spinvals.append(line)
        self.ids.target_product.values = spinvals

        content = self.ids.scrn_contents
        users = self.get_users()
        userstable = DataTable(table=users)
        content.add_widget(userstable)

        # Display Products
        product_scrn = self.ids.scrn_product_contents
        products = self.get_products()
        prod_table = DataTable(table=products)
        product_scrn.add_widget(prod_table)

    def logout(self):
        self.parent.parent.current = 'scrn_si'

    def add_user_fields(self):
        target = self.ids.ops_fields
        target.clear_widgets()
        crud_first = TextInput(hint_text='First Name', multiline=False)
        crud_last = TextInput(hint_text='Last Name', multiline=False)
        crud_user = TextInput(hint_text='User Name', multiline=False)
        crud_pwd = TextInput(hint_text='Password', multiline=False)
        crud_des = Spinner(text='Operator', values=['Operator', 'Administrator'])
        crud_submit = Button(text='Add', size_hint_x=None, width=100,
                             on_release=lambda x: self.add_user(crud_first.text, crud_last.text, crud_user.text,
                                                                crud_pwd.text, crud_des.text))

        target.add_widget(crud_first)
        target.add_widget(crud_last)
        target.add_widget(crud_user)
        target.add_widget(crud_pwd)
        target.add_widget(crud_des)
        target.add_widget(crud_submit)

    def add_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()

        crud_code = TextInput(hint_text='Product Code', multiline=False)
        crud_name = TextInput(hint_text='Product Name', multiline=False)
        crud_weight = TextInput(hint_text='Product Weight', multiline=False)
        crud_stock = TextInput(hint_text='Product In Stock', multiline=False)
        crud_sold = TextInput(hint_text='Products Sold', multiline=False)
        crud_order = TextInput(hint_text='Ordered', multiline=False)
        crud_purchase = TextInput(hint_text='Last Purchase', multiline=False)
        crud_submit = Button(text='Add', size_hint_x=None, width=100,
                             on_release=lambda x: self.add_product(crud_code.text, crud_name.text, crud_weight.text,
                                                                   crud_stock.text, crud_sold.text, crud_order.text,
                                                                   crud_purchase.text))

        target.add_widget(crud_code)
        target.add_widget(crud_name)
        target.add_widget(crud_weight)
        target.add_widget(crud_stock)
        target.add_widget(crud_sold)
        target.add_widget(crud_order)
        target.add_widget(crud_purchase)
        target.add_widget(crud_submit)

    def add_user(self, first, last, user, pwd, des):

        pwd = hashlib.sha256(pwd.encode()).hexdigest()
        if first == '' or last == '' or user == '' or pwd == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)

        else:
            self.mycursor = self.mydb.cursor()
            sql = 'SELECT first_name,last_name,password,user_name FROM users WHERE user_name =%s'
            values = [user]
            self.mycursor.execute(sql, values)
            users = self.mycursor.fetchall()
            
            if users:
                self.notify.add_widget(Label(text='[color=#FF0000][b]Username already existed[/b][/color]', markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch, 1)
            else:

                sql = 'INSERT INTO users(first_name,last_name,user_name,password,designation,date) VALUES (%s,%s,%s,%s,%s,%s)'
                values = [first, last, user, pwd, des, datetime.now()]
                self.mycursor.execute(sql, values)
                self.mydb.commit()
                content = self.ids.scrn_contents
                content.clear_widgets()

                users = self.get_users()
                userstable = DataTable(table=users)
                content.add_widget(userstable)

    def killswitch(self, dtx):
        self.notify.dismiss()
        self.notify.clear_widgets()

    def add_product(self, code, name, weight, stock, sold, order, purchase):

        if code == '' or name == '' or weight == '' or stock == '' or order == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:
            self.mycursor = self.mydb.cursor()
            sql = 'SELECT product_name, product_weight, in_stock, sold, last_purchase, product_code FROM stocks WHERE product_code =%s'
            values = [code]
            self.mycursor.execute(sql, values)
            codes = self.mycursor.fetchall()

            if codes is None:
                self.notify.add_widget(Label(text='[color=#FF0000][b]Invalid Code[/b][/color]', markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch, 1)
            else:
                self.mycursor = self.mydb.cursor()
                sql = 'INSERT INTO stocks(product_code,product_name,product_weight,in_stock,sold,ordered,last_purchase) VALUES (%s,%s,%s,%s,%s,%s,%s)'
                values = [code, name, weight, stock, sold, order, purchase]
                self.mycursor.execute(sql, values)
                self.mydb.commit()
                content = self.ids.scrn_product_contents
                content.clear_widgets()

                prodz = self.get_products()
                stocktable = DataTable(table=prodz)
                content.add_widget(stocktable)

    def update_user_fields(self):
        target = self.ids.ops_fields
        target.clear_widgets()
        crud_first = TextInput(hint_text='First Name', multiline=False)
        crud_last = TextInput(hint_text='Last Name', multiline=False)
        crud_user = TextInput(hint_text='User Name', multiline=False)
        crud_pwd = TextInput(hint_text='Password', multiline=False)
        crud_des = Spinner(text='Operator', values=['Operator', 'Administrator'])
        crud_submit = Button(text='Update', size_hint_x=None, width=100,
                             on_release=lambda x: self.update_user(crud_first.text, crud_last.text, crud_user.text,
                                                                   crud_pwd.text, crud_des.text))

        target.add_widget(crud_first)
        target.add_widget(crud_last)
        target.add_widget(crud_user)
        target.add_widget(crud_pwd)
        target.add_widget(crud_des)
        target.add_widget(crud_submit)

    def update_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()

        crud_code = TextInput(hint_text='Product Code', multiline=False)
        crud_name = TextInput(hint_text='Product Name', multiline=False)
        crud_weight = TextInput(hint_text='Product Weight', multiline=False)
        crud_stock = TextInput(hint_text='Product In Stock', multiline=False)
        crud_sold = TextInput(hint_text='Products Sold', multiline=False)
        crud_order = TextInput(hint_text='Ordered', multiline=False)
        crud_purchase = TextInput(hint_text='Last Purchase', multiline=False)
        crud_submit = Button(text='Update', size_hint_x=None, width=100,
                             on_release=lambda x: self.update_product(crud_code.text, crud_name.text, crud_weight.text,
                                                                      crud_stock.text, crud_sold.text, crud_order.text,
                                                                      crud_purchase.text))

        target.add_widget(crud_code)
        target.add_widget(crud_name)
        target.add_widget(crud_weight)
        target.add_widget(crud_stock)
        target.add_widget(crud_sold)
        target.add_widget(crud_order)
        target.add_widget(crud_purchase)
        target.add_widget(crud_submit)

    def update_user(self, first, last, user, pwd, des):

        pwd = hashlib.sha256(pwd.encode()).hexdigest()
        if user == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:
            self.mycursor = self.mydb.cursor()
            sql = 'SELECT first_name,last_name,password,user_name FROM users WHERE user_name =%s'
            values = [user]
            self.mycursor.execute(sql, values)
            users = self.mycursor.fetchall()
            print(users)
            # users = self.users.find_one({'user_name': user})
            if not users:
                self.notify.add_widget(Label(text='[color=#FF0000][b]Invalid Username[/b][/color]', markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch, 1)
            else:
                for u in users:
                    if first == '':
                        first = u[0]
                    if last == '':
                        last = u[1]
                    if pwd == '':
                        pwd = u[2]
                sql = 'UPDATE users SET first_name=%s,last_name=%s,user_name=%s,password=%s,designation=%s WHERE user_name=%s'
                values = [first, last, user, pwd, des, user]
                self.mycursor.execute(sql, values)
                self.mydb.commit()
                content = self.ids.scrn_contents
                content.clear_widgets()

                users = self.get_users()
                userstable = DataTable(table=users)
                content.add_widget(userstable)

    def update_product(self, code, name, weight, stock, sold, order, purchase):

        if code == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]Code required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:
            self.mycursor = self.mydb.cursor()
            sql = 'SELECT product_name, product_weight, in_stock, sold, last_purchase, product_code FROM stocks WHERE product_code =%s'
            values = [code]
            self.mycursor.execute(sql, values)
            codes = self.mycursor.fetchall()

            if codes is None:
                self.notify.add_widget(Label(text='[color=#FF0000][b]Invalid Code[/b][/color]', markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch, 1)
            else:
                for c in codes:
                    if name == '':
                        name = c[0]
                    if weight == '':
                        weight = c[1]
                    if stock == '':
                        stock = c[2]
                    if sold == '':
                        sold = c[3]
                    if order == '':
                        order = c[4]
                    if purchase == '':
                        purchase = c[5]
                content = self.ids.scrn_product_contents
                content.clear_widgets()

                sql = 'UPDATE stocks SET product_code=%s,product_name=%s,product_weight=%s,in_stock=%s,sold=%s,ordered=%s,last_purchase=%s WHERE product_code=%s'
                values = [code, name, weight, stock, sold, order, purchase, code]
                self.mycursor.execute(sql, values)
                self.mydb.commit()

                prodz = self.get_products()
                stocktable = DataTable(table=prodz)
                content.add_widget(stocktable)

    def remove_user_fields(self):
        target = self.ids.ops_fields
        target.clear_widgets()
        crud_user = TextInput(hint_text='User Name')
        crud_submit = Button(text='Remove', size_hint_x=None, width=100,
                             on_release=lambda x: self.remove_user(crud_user.text))

        target.add_widget(crud_user)
        target.add_widget(crud_submit)

    def remove_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()
        crud_code = TextInput(hint_text='Product Code')
        crud_submit = Button(text='Remove', size_hint_x=None, width=100,
                             on_release=lambda x: self.remove_product(crud_code.text))

        target.add_widget(crud_code)
        target.add_widget(crud_submit)

    def remove_user(self, user):

        if user == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]Enter the product code[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:
            self.mycursor = self.mydb.cursor()
            sql = 'SELECT user_name FROM users WHERE user_name =%s'
            values = [user]
            self.mycursor.execute(sql, values)
            users = self.mycursor.fetchall()

            if not users:
                self.notify.add_widget(Label(text='[color=#FF0000][b]Invalid UserName[/b][/color]', markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch, 1)
            else:
                content = self.ids.scrn_contents
                content.clear_widgets()

                sql = 'DELETE FROM users WHERE user_name=%s'
                values = [user]

                self.mycursor.execute(sql, values)
                self.mydb.commit()

                users = self.get_users()
                userstable = DataTable(table=users)
                content.add_widget(userstable)

    def remove_product(self, code):
        if code == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:

            sql = 'SELECT product_code FROM stocks WHERE product_code =%s'
            values = [code]
            self.mycursor.execute(sql, values)
            codes = self.mycursor.fetchall()
            if not codes:
                self.notify.add_widget(Label(text='[color=#FF0000][b]Invalid Code[/b][/color]', markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch, 1)
            else:
                content = self.ids.scrn_product_contents
                content.clear_widgets()

                sql = 'DELETE FROM stocks WHERE product_code=%s'
                values = [code]

                self.mycursor.execute(sql, values)
                self.mydb.commit()

                prodz = self.get_products()
                stocktable = DataTable(table=prodz)
                content.add_widget(stocktable)

    def get_users(self):
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='root',
            database='pos'
        )

        mycursor = mydb.cursor()

        _users = OrderedDict()
        _users['First Name'] = {}
        _users['Last Name'] = {}
        _users['Username'] = {}
        _users['Passwords'] = {}
        _users['Date'] = {}
        first_names = []
        last_names = []
        user_names = []
        passwords = []
        designations = []

        sql = 'SELECT * FROM users'
        mycursor.execute(sql)
        users = mycursor.fetchall()

        for user in users:
            first_names.append(user[1])
            last_names.append(user[2])
            user_names.append(user[3])
            pwd = user[4]
            if len(pwd) > 10:
                pwd = pwd[:10] + '...'
            passwords.append(pwd)
            designations.append(user[5])
        # print(designations)
        users_length = len(first_names)
        idx = 0
        while idx < users_length:
            _users['First Name'][idx] = first_names[idx]
            _users['Last Name'][idx] = last_names[idx]
            _users['Username'][idx] = user_names[idx]
            _users['Passwords'][idx] = passwords[idx]
            _users['Date'][idx] = designations[idx]

            idx += 1

        return _users

    def get_products(self):
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='root',
            database='pos',
            auth_plugin='mysql_native_password'
        )
        self.mycursor = mydb.cursor()
        _stocks = OrderedDict()
        _stocks['Product Code'] = {}
        _stocks['Product Name'] = {}
        _stocks['Stock'] = {}
        _stocks['Sold'] = {}
        
        product_code = []
        product_name = []
        in_stock = []
        sold = []
        
        sql = 'SELECT * FROM stocks'
        self.mycursor.execute(sql)
        products = self.mycursor.fetchall()

        for product in products:
            product_code.append(product[1])
            name = str(product[2])
            if len(name) > 10:
                name = name[:10] + '...'
            product_name.append(name)
            
            in_stock.append(product[3])
            try:
                sold.append(product[4])
            except KeyError:
                sold.append('')
            
            
        
        products_length = len(product_code)
        idx = 0
        while idx < products_length:
            _stocks['Product Code'][idx] = product_code[idx]
            _stocks['Product Name'][idx] = product_name[idx]
           
            _stocks['Stock'][idx] = in_stock[idx]
            _stocks['Sold'][idx] = sold[idx]
            

            idx += 1

        return _stocks

    def view_stats(self):
       pass

    def change_screen(self, instance):
        if instance.text == 'Manage Products':
            self.ids.scrn_mngr.current = 'scrn_product_content'
        elif instance.text == 'Manage Users':
            self.ids.scrn_mngr.current = 'scrn_content'
        else:
            self.ids.scrn_mngr.current = 'scrn_analysis'


class AdminApp(App):
    def build(self):
        return AdminWindow()


if __name__ == '__main__':
    AdminApp().run()
