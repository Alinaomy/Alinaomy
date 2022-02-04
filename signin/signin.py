from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
import mysql.connector
import hashlib

Builder.load_file('signin/signin.kv')


class SigninWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def validate_user(self):
        self.mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='root',
            database='pos'
        )

        self.mycursor = self.mydb.cursor()
        # sql = 'SELECT * FROM stocks'
        # self.mycursor.execute(sql)
        # products = self.mycursor.fetchall()

        user = self.ids.username_field
        pwd = self.ids.pwd_field
        info = self.ids.info

        uname = user.text
        passw = pwd.text

        if uname == '' or passw == '':
            info.text = '[color=#FF0000]username and/or password required [/color]'

        else:
            sql = 'SELECT user_name, password, designation FROM users WHERE user_name=%s'
            values = [uname]
            self.mycursor.execute(sql, values)
            users = self.mycursor.fetchall()

            if users == None:
                info.text = '[color=#00FF000]Invalid Username[/color]'
            else:
                passw = hashlib.sha256(passw.encode()).hexdigest()
                for u in users:
                    if passw == u[2]:
                        des = u[3]
                        if des == 'Administrator':
                            info.text = '[color=#00FF000]Logged successfully [/color]'
                            self.parent.parent.current = 'scrn_admin'
                        else:
                            self.parent.parent.current = 'scrn_op'
                    else:
                        info.text = '[color=#FF0000]Incorrect password required [/color]'


class SigninApp(App):
    def build(self):
        return SigninWindow()


if __name__ == "__main__":
    sa = SigninApp()
    sa.run()
