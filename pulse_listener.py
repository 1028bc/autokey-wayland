import evdev, time, sys, threading, queue, select, json, os

VERSION = "1.0 [Fail-Safe]"
DB_FILE = os.path.expanduser("~/triggers.json")

def load_db():
    try:
        with open(DB_FILE, 'r') as f: return json.load(f)
    except: return {"abbreviations": {}, "hotkeys": {}}

DB = load_db()
job_queue = queue.Queue()

MOD_MAP = {29: 'ctrl', 97: 'ctrl', 56: 'alt', 100: 'alt', 42: 'shift', 54: 'shift'}
KEYMAP = {**{chr(i): (getattr(evdev.ecodes, f'KEY_{chr(i).upper()}'), 0) for i in range(97, 123)},
          **{chr(i): (getattr(evdev.ecodes, f'KEY_{chr(i)}'), 1) for i in range(65, 91)},
          **{str(i): (getattr(evdev.ecodes, f'KEY_{i}'), 0) for i in range(10)},
          ' ': (evdev.ecodes.KEY_SPACE, 0), '\n': (evdev.ecodes.KEY_ENTER, 0),
          ':': (evdev.ecodes.KEY_SEMICOLON, 1), ';': (evdev.ecodes.EV_KEY, evdev.ecodes.KEY_SEMICOLON, 0), 
          '.': (evdev.ecodes.KEY_DOT, 0), '/': (evdev.ecodes.KEY_SLASH, 0)}

def type_string(ui, text):
    for char in text:
        if char in KEYMAP:
            if isinstance(KEYMAP[char], tuple):
                keycode, shift = KEYMAP[char]
                if shift: ui.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTSHIFT, 1)
                ui.write(evdev.ecodes.EV_KEY, keycode, 1); ui.write(evdev.ecodes.EV_KEY, keycode, 0)
                if shift: ui.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_LEFTSHIFT, 0)
            else:
                ui.write(evdev.ecodes.EV_KEY, KEYMAP[char], 1); ui.write(evdev.ecodes.EV_KEY, KEYMAP[char], 0)
            ui.syn(); time.sleep(0.01)

def worker(ui):
    global DB
    while True:
        try:
            job = job_queue.get()
            if job is None: break
            
            # ATOMIC FLUSH: Instant virtual release, no blocking loops
            for code in [29, 97, 56, 100, 42, 54, 125, 126]:
                ui.write(evdev.ecodes.EV_KEY, code, 0)
            ui.syn(); time.sleep(0.1)

            if job.get('type') == "RELOAD": 
                DB = load_db(); print("[SYSTEM] Reloaded."); job_queue.task_done(); continue

            if job.get('len', 0) > 0:
                for _ in range(job['len']):
                    ui.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_BACKSPACE, 1)
                    ui.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_BACKSPACE, 0)
                    ui.syn(); time.sleep(0.01)

            type_string(ui, job['payload'])
            job_queue.task_done()
        except: job_queue.task_done()

def main():
    targets = [evdev.InputDevice(p) for p in evdev.list_devices() if "keyboard" in evdev.InputDevice(p).name.lower()]
    if not targets: return
    ui = evdev.UInput.from_device(targets[0], name="PulseBridge-Core")
    for dev in targets: dev.grab()

    threading.Thread(target=worker, args=(ui,), daemon=True).start()
    dev_map = {d.fd: d for d in targets}
    abbr_buf = []
    active_mods = set()
    
    print(f"[PulseBridge] {VERSION} ONLINE.")
    try:
        while True:
            r, _, _ = select.select(dev_map.keys(), [], [])
            for fd in r:
                for event in dev_map[fd].read():
                    if event.type == evdev.ecodes.EV_KEY:
                        intercepted = False
                        if event.value == 1: # Down
                            if event.code in MOD_MAP: active_mods.add(event.code)
                            current_mods = {MOD_MAP[m] for m in active_mods if m in MOD_MAP}
                            
                            for name, hk in DB.get("hotkeys", {}).items():
                                parts = [p.strip().lower() for p in name.split('+')]
                                hk_mods = set(parts[:-1])
                                if event.code == hk["key"] and hk_mods.issubset(current_mods):
                                    job_queue.put({'type': hk['type'], 'payload': hk['payload'], 'len': 0})
                                    intercepted = True; break
                            
                            if not intercepted and 'ctrl' in current_mods and 'alt' in current_mods:
                                if event.code == evdev.ecodes.KEY_R: job_queue.put({'type': 'RELOAD'}); intercepted = True
                                elif event.code == evdev.ecodes.KEY_ESC: return
                            
                            if not intercepted:
                                abbr_buf.append(event.code); abbr_buf = abbr_buf[-10:]
                                for abbr, data in DB.get("abbreviations", {}).items():
                                    if tuple(abbr_buf[-len(data['codes']):]) == tuple(data['codes']):
                                        job_queue.put({'type': data['type'], 'payload': data['payload'], 'len': len(data['codes'])-1})
                                        abbr_buf = []; intercepted = True; break
                        
                        elif event.value == 0: # Up
                            if event.code in MOD_MAP: active_mods.discard(event.code)

                        if not intercepted:
                            ui.write(evdev.ecodes.EV_KEY, event.code, event.value); ui.syn()
    finally:
        for dev in targets:
            try: dev.ungrab()
            except: pass
if __name__ == "__main__": main()
