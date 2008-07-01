import sqlite3

db = 'erebus.db'


def getExchangeId(ical_uid):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    r = c.execute(
        "select soap_id, soap_chkey from items where icalendar_id=?",
        (ical_uid,))

    row = r.fetchone()

    if not row:
        return None

    conn.commit()
    conn.close()

    return row # (soap_id, soap_chkey) is the format we use

def setExchangeId(ical_uid, exchangeId):
    ex_id, ex_chkey = exchangeId

    if getExchangeId(ical_uid):
        raise AttributeError, "%s already exists in database" % ical_uid

    conn = sqlite3.connect(db)
    c = conn.cursor()

    r = c.execute(
        'insert exchange_id, soap_id, soap_chkey into items values (?,?,?)',
        (ical_uid, ex_id, ex_chkey))

    conn.commit()
    conn.close()
              

def getItemId(icalendar_id=None,exchange_id=None,fallback=None):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    if icalendar_id:
        r = c.execute('select id from items where icalendar_id = ?', (icalendar_id,))
        item_id = fetchone()
        if item_id: item_id = item_id[0]
    elif exchange_id:
        ex_id, ex_chkey = exchange_id
        r = c.execute('select id from items where soap_id = ? and soap_chkey = ?',
                      (ex_id, ex_chkey))
        item_id = fetchone()
        if item_id: item_id = item_id[0]

    conn.close()
    return item_id


def getICalFields(item_id=None,icalendar_id=None,exchange_id=None):

    conn = sqlite3.connect(db)
    c = conn.cursor()

    item_id = getItemId(icalendar_id,exchange_id,item_id)

    if not item_id:
        return None

    r = c.execute(
        'select icalendar_field, icalendar_value from icalendar_fields where parent_id = ?',
        (item_id,))

    conn.commit()
    conn.close()
    return r.fetchall()
    

def setICalFields(item_id=None,icalendar_id=None,exchange_id=None,fields=[]):

    conn = sqlite3.connect(db)
    c = conn.cursor()

    item_id = getItemId(icalendar_id,exchange_id,item_id)

    if not item_id: return None

    r = c.execute('delete from icalendar_fields where parent_id = ?', (item_id,))

    for k,v in fields:
        r = c.execute(
            "insert into icalendar_fields (parent_id,icalendar_field,icalendar_value) (?,?,?)",
            (item_id, k, v));

    conn.commit()
    conn.close()

def insertICalFields(ical):
    """
    Inserts necessary ical fields into db
    """
    pass


#####
# Misc. iCalendar conversion functions
#

def class2sensitivity(cl):
    sens = { 'PUBLIC'       : 'Normal',
             'PRIVATE'      : 'Private',
             'CONFIDENTIAL' : 'Confidential' }

    if sens.has_key(cl): return sens[cl]
    else:                return None

def sensitivity2class(s):
    cs = { 'Normal'         : 'PUBLIC',
           'Personal'       : 'PRIVATE', # loosing information here.
           'Private'        : 'PRIVATE',
           'Confidential'   : 'CONFIDENTIAL' }

    if cs.has_key(s): return cs[s]
    else:             return None

def vDDD2dt(vd):
    return vd.dt

