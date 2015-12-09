#=============================================================================
#
# file :        ldap_login.py
#
# description : Python module to allow LDAP validation and logging
#
# $Author:      mbroseta@cells.es
#
# $Revision:    1.0
#
# copyleft :    ALBA CELLS Synchrotron 
#               Ctra. BP. 1413 km 3,308290
#               Cerdanyola del Valles
#               Barcelona (Spain)
#
#=============================================================================

from PyQt4 import Qt, QtGui,QtCore

import os, sys
import ldap
import logging
import logging.handlers

__LDAP_SERVER__ = ['ldap://ldap01.cells.es','ldap://ldap02.cells.es','ldap://ldap03.cells.es']
__LDAP_WHO_TEMPLATE__ = 'uid=%s,ou=People,dc=CELLS,dc=ES'

class InputLineEdit(Qt.QWidget):
    def __init__(self, parent, row, text, echo_mode=Qt.QLineEdit.Normal):
        Qt.QWidget.__init__(self, parent)
        #self.parent = parent

        self.label = Qt.QLabel(text)
        self.line_edit = Qt.QLineEdit()
        self.line_edit.setMinimumSize(QtCore.QSize(120, 25))        
        self.line_edit.setEchoMode(echo_mode)

        self.parent().layout().addWidget(self.label, row, 1)
        self.parent().layout().addWidget(self.line_edit, row, 2)

class LdapLogin(Qt.QDialog):
    def __init__(self, parent=None):
        Qt.QDialog.__init__(self, parent)
        self.username = ''

        self.setLayout(Qt.QGridLayout())
        message = 'LDAP Login requested\nPlease enter your user name and password'
        self.layout().addWidget(Qt.QLabel(message),0,1,1,3)
        
        self.label = QtGui.QLabel()
        self.label.setMinimumSize(QtCore.QSize(80, 80))
        self.label.setMaximumSize(QtCore.QSize(80, 80))

        self.label.setPixmap(QtGui.QPixmap(os.path.abspath(os.path.dirname(__file__))+"/password.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label_186")
        self.layout().addWidget(self.label, 0, 0, 4, 1)
        
        self.user = InputLineEdit(self, 1, 'User', Qt.QLineEdit.Normal)
        self.password = InputLineEdit(self, 2, 'Password', Qt.QLineEdit.Password)
        
        self.okbutton = QtGui.QPushButton("&Ok")
        self.okbutton.setMaximumSize(QtCore.QSize(80,30))
        self.layout().addWidget(self.okbutton,4,1,1,1)
        
        self.cancelbutton = QtGui.QPushButton("&Cancel")
        self.cancelbutton.setMaximumSize(QtCore.QSize(80,30))
        self.layout().addWidget(self.cancelbutton,4,2,1,1)
        
        #self.connect(self.password.line_edit, Qt.SIGNAL('returnPressed()'), self.validate)
        self.connect(self.okbutton, QtCore.SIGNAL("clicked()"), self.validate)
        self.connect(self.cancelbutton, QtCore.SIGNAL("clicked()"), self.exit)        
        self.connect(self, Qt.SIGNAL('finished(int)'), self.erasePassword)
        
        # Defualt allowed users
        self.allowed_users = ["sicilia"]
        
        # Init variables used fro the logging
        self.logEnabled = False
        self.logmsg = ""
        

    def validate(self):
        user = str(self.user.line_edit.text())
        passwd = str(self.password.line_edit.text())
            
        errormsg = ''
        for server in __LDAP_SERVER__:
            try:
                con = ldap.initialize(server)
                con.start_tls_s()
                who = __LDAP_WHO_TEMPLATE__ % user
                con.bind_s(who, passwd)
                self.username = user
                if user not in self.allowed_users:
                    self.done(Qt.QDialog.Rejected)                            
                    QtGui.QMessageBox.critical(self, self.tr("Process Management"),
                                               "User not allowed")      
                else:
                    self.done(Qt.QDialog.Accepted)
                    if self.logEnabled:
                        msg = "User: %s --> "%user+self.logmsg
                        self.my_logger.info(msg)
                        self.logmsg = ""                    
                self.clear()
                return user
            except ldap.INVALID_CREDENTIALS:
                self.password.label.setStyleSheet('QLabel { color: red }')
                self.password.line_edit.selectAll()
                errormsg = "Your username or password is incorrect"
                break
            except ldap.LDAPError, e:
                errormsg = e.args[0]['desc']
        QtGui.QMessageBox.critical(self, self.tr("Process Management"),errormsg)
        self.clear()
        return False

    def clear(self):
        self.password.line_edit.setText('')
        self.user.line_edit.setText('')
        self.user.line_edit.setFocus()

    def exit(self):
        self.clear()
        self.done(Qt.QDialog.Rejected)

    def erasePassword(self):
        # PLEASE, DO NOT HACK IN HERE...
        self.password.line_edit.setText('Forget it!')
        self.clear()
        
    #def getUser(self):
        #return str(self.user.line_edit.text())
    
    def setAllowedUsers(self, userlist):
        # userlist is the list of users to check if are allowed
        if len(userlist)>0:
            self.allowed_users=userlist
            
    def getAllowedUsers(self):
        # userlist is the list of users to check if are allowed
        return self.allowed_users
    
    def setLogging(self, st=True, filename=""):
        #Logging control
        if self.logEnabled != st:
            self.logEnabled = st
            if self.logEnabled:    
                if filename == "":
                    filename = 'validation.log'
                
                self.my_logger = logging.getLogger('VALIDATION')
                self.my_logger.setLevel(logging.DEBUG)
                
                handler = logging.handlers.RotatingFileHandler(filename, maxBytes=5000000, backupCount=5)
                handler.setLevel(logging.INFO)
                
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
                handler.setFormatter(formatter)
                
                self.my_logger.addHandler(handler)
                
    def setLogMessage(self, txt):
        self.logmsg = txt      

def main():
    import sys
    
    app= QtGui.QApplication(sys.argv)  
    
    task = LdapLogin()
    task.setLogging(True,"Prueba.log")
    
    task.setLogMessage("This is a test message")
    if task.exec_() != 0:
        print "\n*** %s is a valid user *** \n"%task.getUser()
    else:
        print "\n** User %s Rejected ** \n"%task.getUser()
    
    
    sys.exit(-1)
    
if __name__ == '__main__':
    main()