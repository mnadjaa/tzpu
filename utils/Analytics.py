import math
from collections import defaultdict
from datetime import datetime
import json
import os  # Dodat import

from entities.EventType import EventType
from entities.User import User
# from utils.DatabaseUtils import DatabaseUtils # UKLONJENO
from utils.Proprerties import Properties


class Analytics:
    # ----------------------------------------------------
    # PARAMETRI I KEŠ ZA LOGOVANJE (IZ DATABASEUTILS)
    # ----------------------------------------------------
    fileWrites = {
        "LOGS/Events.csv": "",
        "LOGS/Simulation.csv": "",
        "LOGS/Properties.csv": "",
        "LOGS/Important.txt": ""
    }

    def __init__(self):
        # self.database = DatabaseUtils() # UKLONJENO
        self.log_to_database = True  # Logika za logovanje je sada ugrađena
        self.total_user_count = 0
        self.users_served_count = 0
        self.utilization = 0

        self.SLA1_broke = 0
        self.SLA2_broke = 0
        self.SLA3_broke = 0
        self.SLA4_broke = 0

    arrivals = defaultdict(lambda: 0)
    utilization_percent = defaultdict(lambda: [])
    waits_for_getting = defaultdict(lambda: [])

    # ----------------------------------------------------
    # UGRAĐENE METODE ZA LOGOVANJE (IZ DATABASEUTILS)
    # ----------------------------------------------------

    def clear_logs(self):
        """Metoda clear preimenovana u clear_logs da bi se izbegao konflikt."""
        Analytics.fileWrites = {
            "LOGS/Events.csv": "",
            "LOGS/Simulation.csv": "",
            "LOGS/Properties.csv": "",
            "LOGS/Important.txt": ""
        }

    def _write(self, file, str_):
        """Interna metoda za keširanje stringova pre upisa u fajl."""
        Analytics.fileWrites[file] += str_

    def writeAll(self):
        """Upisuje sav keširani sadržaj u odgovarajuće fajlove."""
        print("LOGGING ALL DATA TO FILES...")
        for file, str_ in Analytics.fileWrites.items():
            if not str_:
                continue  # Preskoči prazne fajlove

            # Poseban tretman za Important.txt (dodavanje sufiksa)
            final_file = file
            if file == "LOGS/Important.txt":
                final_file = f"LOGS/Important{Properties.IMPORTANT_TXT_SUFFIX}.txt"

            # Proverava da li direktorijum LOGS postoji pre upisa
            os.makedirs(os.path.dirname(final_file), exist_ok=True)

            with open(final_file, "a") as myfile:
                myfile.write("\n" + str_)
        print("LOGGING COMPLETE.")

    # ------------------ LOGGING METODE KOJE KORISTI MAIN.PY -------------------

    # Ekvivalent WriteEvent
    def WriteEvent(self, event_type: str, simulation_uuid: str, user_id: str, timestamp: str, duration: str):
        self._write("LOGS/Events.csv",
                    f"{simulation_uuid}, {event_type}, User:{user_id}, Time:{timestamp}, Value:{duration}\n")

    # Ekvivalent WriteSimulation
    def WriteSimulation(self, simulation_uuid: str):
        self._write("LOGS/Simulation.csv", f"{simulation_uuid}\n")

    # Ekvivalent WriteProperties
    def WriteProperties(self, simulation_uuid: str, type_: str, value: str):
        self._write("LOGS/Properties.csv", f"{simulation_uuid}, {type_}, {value}\n")

    # Ekvivalent WriteImportant
    def WriteImportant(self, txt: str, preTxt: str = "", toPrint=False):
        if (type(txt) == bool): txt = "true" if txt else "false"
        if (type(txt) == list): txt = json.dumps(txt)

        if (preTxt == None):
            self._write("LOGS/Important.txt", f"{txt}\n")
        else:
            self._write("LOGS/Important.txt", f"\"{preTxt}\":{txt},\n")

        if toPrint: print(f"{preTxt}{txt}")

    def log_event(self, event_type, user_id, time, duration):
        """Loguje pojedinačni događaj."""
        print(f"EVENT: {event_type}")
        self.WriteEvent(event_type, Properties.SIMULATION_UUID, user_id, time, duration)

    def log_simulation_start(self):
        """Loguje početak simulacije i parametre."""
        self.WriteSimulation(Properties.SIMULATION_UUID)
        self.log_simulation_parameters()

    def log_simulation_parameters(self):
        """Loguje sve sistemske parametre u fajl Properties.csv."""
        for name, value in Properties.get_parameters():
            self.WriteProperties(Properties.SIMULATION_UUID, name, value)

    # ----------------------------------------------------
    # ORIGINALNE METODE ZA ANALITIKU (IZVORNO IZ ANALYTICS)
    # ----------------------------------------------------

    def register_arrivals(self, time):
        self.arrivals[int(time)] += 1

    def system_utilization(self, time, wait):
        self.utilization_percent[int(time)].append(wait)

    def register_utilization(self, time, max_num, current_num):
        self.utilization = current_num / max_num
        self.system_utilization(time, self.utilization * 100)
        if self.log_to_database:
            self.log_event(EventType.SYSTEM_UTILIZATION.value, None, time, round(self.utilization * 100))

    def register_user_login(self, time, user: User):
        self.register_arrivals(time)
        self.total_user_count += 1
        print(f"User({user.user_id}) login at {time}")

    def register_usage_time(self, begin, end, user: User):
        usage_time = end - begin

        print(f"User {user.name}({user.user_id}) used resource for {usage_time} minutes")

        self.users_served_count += 1
        print(
            f"Users finished: {self.users_served_count} of total {self.total_user_count} users; Utilization: {self.utilization}")
        if self.log_to_database:
            self.log_event(EventType.RESOURCE_USAGE.value, user.user_id, end, usage_time * 1000)

    def register_user_waiting(self, queue_begin, queue_end, user: User):
        wait = queue_end - queue_begin
        print(f"USER WAIT [{wait}]")
        print(wait)
        self.register_wait_for_getting(queue_end, wait)

        # Logika provere SLA granica... (ostavljena nepromenjena)
        if wait > Properties.SLA1:
            self.SLA1_broke += 1
            if wait > Properties.SLA2:
                self.SLA2_broke += 1
                if wait > Properties.SLA3:
                    self.SLA3_broke += 1
                    if wait > Properties.SLA4:
                        self.SLA4_broke += 1
                        print(f"User({user.user_id}) waited {wait} minutes and broke SLA: {Properties.SLA4}!")
                        print(f"SLA was broken {self.SLA4_broke} times during this simulation")
                        self.log_event(EventType.SLA_BROKE.value, user.user_id, queue_end, Properties.SLA4)
                    else:
                        print(f"User({user.user_id}) waited {wait} minutes and broke SLA: {Properties.SLA3}!")
                        print(f"SLA was broken {self.SLA3_broke} times during this simulation")
                        self.log_event(EventType.SLA_BROKE.value, user.user_id, queue_end, Properties.SLA3)
                else:
                    print(f"User({user.user_id}) waited {wait} minutes and broke SLA: {Properties.SLA2}!")
                    print(f"SLA was broken {self.SLA2_broke} times during this simulation")
                    self.log_event(EventType.SLA_BROKE.value, user.user_id, queue_end, Properties.SLA2)
            else:
                print(f"User({user.user_id}) waited {wait} minutes and broke SLA: {Properties.SLA1}!")
                print(f"SLA was broken {self.SLA1_broke} times during this simulation")
                self.log_event(EventType.SLA_BROKE.value, user.user_id, queue_end, Properties.SLA1)

        print(f"User({user.user_id}) waited {wait} minutes")
        if self.log_to_database:
            self.log_event(EventType.USER_WAIT.value, user.user_id, queue_end, wait)

    def register_wait_for_getting(self, time, wait):
        self.waits_for_getting[int(time)].append(wait)

    def register_new_resource_prepared(self, resource_count, time):
        print(f"RESOURCE COUNT {resource_count}")
        if self.log_to_database:
            self.log_event(EventType.RESOURCE_COUNT.value, None, time, resource_count)