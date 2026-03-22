import json, sys, os

DB_FILE = os.path.expanduser("~/triggers.json")
MAP = {'a':30,'b':48,'c':46,'d':32,'e':18,'f':33,'g':34,'h':35,'i':23,'j':36,'k':37,'l':38,'m':50,
       'n':49,'o':24,'p':25,'q':16,'r':19,'s':31,'t':20,'u':22,'v':47,'w':17,'x':45,'y':21,'z':44,
       '1':2,'2':3,'3':4,'4':5,'5':6,'6':7,'7':8,'8':9,'9':10,'0':11,';':39,'/':98,'.':52,',':51,
       '[':26,']':27,'ctrl':29,'alt':56,'shift':42}

def load_db():
    if not os.path.exists(DB_FILE): return {"abbreviations": {}, "hotkeys": {}}
    with open(DB_FILE, 'r') as f: return json.load(f)

def save_db(db):
    with open(DB_FILE, 'w') as f: json.dump(db, f, indent=4)

db = load_db()
cmd = sys.argv[1] if len(sys.argv) > 1 else "list"

if cmd == "add" and len(sys.argv) > 4:
    abbr, mode, payload = sys.argv[2], sys.argv[3], sys.argv[4]
    db["abbreviations"][abbr] = {"codes": [MAP[c] for c in abbr if c in MAP], "type": mode, "payload": payload}
    save_db(db); print(f"ADDED: {abbr}")

elif cmd == "add-hk" and len(sys.argv) > 4:
    combo, mode, payload = sys.argv[2], sys.argv[3], sys.argv[4]
    # Normalize: strip spaces and lowercase for perfect matching
    norm_combo = "+".join([p.strip().lower() for p in combo.split('+')])
    parts = norm_combo.split('+')
    db["hotkeys"][norm_combo] = {"key": MAP[parts[-1]], "type": mode, "payload": payload}
    save_db(db); print(f"ADDED HOTKEY: {norm_combo}")

elif cmd == "del" and len(sys.argv) > 2:
    target = sys.argv[2].strip().lower()
    if target in db["abbreviations"]: del db["abbreviations"][target]
    elif target in db["hotkeys"]: del db["hotkeys"][target]
    save_db(db); print(f"DELETED: {target}")

else:
    print(f"Abbrev: {list(db['abbreviations'].keys())}")
    print(f"Hotkey: {list(db['hotkeys'].keys())}")
