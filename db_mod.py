import os
import sys
import sqlite3
import pickle



class MiroDatabase():
    """Connect to the miro database and set or retrieve values.

    """

    def get_db_location(self):
        if sys.platform.startswith("darwin"):
            mirodb = os.path.join(os.getenv("HOME"),"Library","Application Support","Miro","sqlitedb")
        elif sys.platform.startswith("linux"):
            mirodb = os.path.join(os.getenv("HOME"),".miro","sqlitedb")
        elif sys.platform.startswith("win"):
            winver = sys.getwindowsversion()[0]
            print winver
            if int(winver) < 6: #WinXP
                mirodb = os.path.join(os.getenv("HOME"),"Application Data","Participatory Culture Foundation","Miro","Support","sqlitedb")
            else: #Vista or Windows7
                mirodb = os.path.join(os.getenv("HOME"),"AppData","Roaming","Participatory Culture Foundation","Miro","Support","sqlitedb")
            print mirodb
        else:
            print "no idea what is db"
            
        return mirodb

    def get_value(self,table,field):
        database = self.get_db_location()
        conn = sqlite3.connect(database)
        stmt = "select "+field+" from " +table
        c = conn.cursor()
        c.execute(stmt)
        myval = c.fetchone()[0]
        conn.close()
        ofile = os.path.join(os.getenv("PCF_TEST_HOME"),"Miro","dbval.pkl")
        output = open(ofile, 'wb')
        pickle.dump(str(myval), output)
        output.close()
        


    def set_value(self,table,field,val):
        database = self.get_db_location()
        conn = sqlite3.connect(database)
        v = (val,)
        conn.execute('update '+table+' set '+field+'=?',v)
        conn.commit()       
        conn.close()


if __name__ == '__main__':
    md =  MiroDatabase()
##    md.set_value("global_state","tabs_width",300)
    md.get_value("global_state","tabs_width")



        
