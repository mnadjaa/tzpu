import uuid

from matplotlib.pyplot import margins
from simpy import RealtimeEnvironment

from entities.Broker import Broker
from entities.BrokerNoPreparing import BrokerNoPreparing
from entities.BrokerPrepareWhenZero import BrokerPrepareWhenZero
from entities.EventType import EventType
from entities.ResourceProvider import ResourceProvider
from entities.User import User
from entities.UserScheduler import UserScheduler
from utils.Analytics import Analytics
from utils.Graphs import Graphs
from utils.DisplayLog import DisplayLog
from utils.Proprerties import Properties
from utils.Options import Options

import csv
import simpy
import json
import time
import tkinter as tk

import numpy as np
import random
import sys

from datetime import datetime
#import threading
import os
import time

SEED = 422
ui = False  #ovde dal hoces UI tj. da se prikazuju grafici

_arrival_pattern = None
_broker_choice = None
_initial_wave = None
#_sla = None
_resurs_mean = None
_resurs_std = Options.RESOURCE_PREPARE_TIME_STD_OPTS
_set_raspodela = None
pocetne_vrednosti = [0, 0, 0, 0, True] #mean, arrival, broker, set, initial

OUTPUT_CSV_FILE = "rezultatiBroker=2.csv"
_single_run = False
one_important_txt = False

_i_ = 0
args = list(map(lambda x: x.lower(), sys.argv[1:]))#argumenti prosledjeni preko komandne liniej
while _i_ < len(args):
    if(args[_i_]=="seed"):
        SEED = int(args[_i_+1])
        _i_+=1
    #if(args[_i_]=="u" or args[_i_]=="ui"):    #elif
     #   ui = ((args[_i_+1])[0]=="t" or (args[_i_+1])[0]=="y" or (args[_i_+1])[0]=="true")
      #  _i_+=1
    elif(args[_i_]=="i" or args[_i_]=="iw" or args[_i_]=="initial_wave"):
        _initial_wave = ((args[_i_+1])[0]=="t" or (args[_i_+1])[0]=="y" or (args[_i_+1])[0]=="true")
        _i_+=1
    elif(args[_i_]=="one_txt"):
        one_important_txt = True
    elif(args[_i_]=="one_txt_f"):
        one_important_txt = False
    elif(args[_i_]=="e" or args[_i_]=="exit"):
        _single_run = True
    elif(args[_i_]=="broker" or args[_i_]=="b"):
        _broker_choice = int(args[_i_+1])
        _i_+=1
    elif(args[_i_]=="arrival" or args[_i_]=="a"):
        _arrival_pattern = int(args[_i_+1])
        _i_+=1
    # elif(args[_i_]=="sla" or args[_i_]=="s"):
    #     _sla = float(args[_i_+1])
    #     _i_+=1
    elif(args[_i_]=="set" or args[_i_]=="s_r"):
        _set_raspodela = int(args[_i_+1])
        _i_+=1
    elif(args[_i_]=="resurs_mean" or args[_i_]=="r_m"):
        _resurs_mean = float(args[_i_+1])
        _i_+=1
    elif(args[_i_]=="resurs_std" or args[_i_]=="r_s"):
        _resurs_std = float(args[_i_+1])
        _i_+=1
    elif(args[_i_]=="ready_count" or args[_i_]=="r_c"):
        Properties.READY_COUNT = int(args[_i_+1])
        _i_+=1
    elif(args[_i_]=="max_available_resources" or args[_i_]=="m_a_r"):
        Properties.MAX_AVAILABLE_RESOURCES = int(args[_i_+1])
        _i_+=1
    elif(args[_i_]=="critical_utilisation_percent" or args[_i_]=="c_u_p"):
        Properties.CRITICAL_UTILISATION_PERCENT = float(args[_i_+1])
        _i_+=1
    elif(args[_i_]=="resource_add_number" or args[_i_]=="r_a_n"):
        Properties.RESOURCE_ADD_NUMBER = int(args[_i_+1])
        _i_+=1
    elif (args[_i_] == "u_c" or args[_i_] == "user_count"):  # <--- DODATO
        Properties.USER_COUNT = int(args[_i_ + 1])
        _i_ += 1
    else:
        print(f"Bad argument: {args[_i_]}")
        sys.exit()
    _i_+=1




main = None
graph = None
user_scheduler = None
#database = None
analytics = None
canvas = None
log = None
print(f"ui= {ui}")

if ui:
    main = tk.Tk()
    main.title("Simulation")
    main.config(bg="#fff")
    top_frame = tk.Frame(main)
    top_frame.pack(side=tk.TOP, expand=False)
    canvas = tk.Canvas(main, width=1300, height=350, bg="white")
    canvas.pack(side=tk.TOP, expand=False)
############################################
# def rnd(tp,idx=None):
#     return random.choice(tp) if(idx==None) else tp[idx]
# # Tp
# Properties.RESOURCE_PREPARE_TIME_MEAN = random.uniform(0.5,8)
# Properties.RESOURCE_PREPARE_TIME_STD = random.uniform(0.1,0.3)
# # SLA kriterijumi
# Properties.SLA = rnd((0.1, 0.5, 1, 1.5))
# # arrival pattern

# if(arrival_pattern == None):
#     print("Choose arrival pattern option (1, 2, 3)")
#     Properties.ARRIVAL_PATTERN = int(input())
# else:
#     Properties.ARRIVAL_PATTERN = arrival_pattern

# if(broker_choice == None):
#     print("Choose broker option (1, 2, 3) "
#         "1=Broker(CriticalUserPercent) "
#         "2=PrepareWhenZero "
#         "3=NoPreparing")
#     Properties.BROKER_TYPE = int(input())
# else:
#     Properties.BROKER_TYPE = broker_choice

# if(initial_wave == None):
#     print("Is initial wave known (y/N)")
#     y_n = input()
#     if y_n == "y" or y_n == "Y":
#         Properties.INITIAL_WAVE_KNOWN = True
#     else:
#         Properties.INITIAL_WAVE_KNOWN = False
# else:
#     Properties.INITIAL_WAVE_KNOWN = initial_wave

## option 1
##Properties.USER_COUNT = 300
##Properties.NEXT_LOGIN_MEAN = rnd((90,120))
##Properties.USERS_PER_LOGIN_MEAN = rnd((20,35))

## option 2
#Properties.USER_COUNT = 100  # 300
#### T = 0
##Properties.USERS_PER_LOGIN_MEAN = rnd((20,35,100))
#### T>0
##Properties.USERS_PER_LOGIN_MEAN = rnd((3,5,8))

## option 3
#### csv = xlsx ?
# usage time
#### xlsx     - ovde se ucitavaju raspodele one
# aspekti
## poznatost T=0
#### option 1
#### option 2
## broker algoritam
#### Broker
#### BrokerPrepareWhenZero
#### BrokerNoPreparing
# kriterijumi optimizacije
## option 1:  ukupno vreme resursa min
## option 2:  pool size min

############################################

DONE = True
def create_clock(environment):
    while not DONE:
        yield environment.timeout(1)
        if ui and graph:
            graph.tick(environment.now)


def start_simulation(env: RealtimeEnvironment, broker, user_scheduler,opcije):
    Properties.SIMULATION_UUID = str(uuid.uuid4())
    print(Properties.SIMULATION_UUID)

    user_id = 1
    next_person_id = 0

    analytics.WriteImportant(f"\n{'{'}\n\"id\":\"{Properties.SIMULATION_UUID}\",\"time\":\"{datetime.now()}\",",None)
    analytics.WriteImportant(opcije,"opcije")
    analytics.WriteImportant(SEED,"SEED")
    #database.WriteImportant(Properties.SLA,"SLA")
    analytics.WriteImportant(Properties.ARRIVAL_PATTERN,"ARRIVAL_PATTERN")
    analytics.WriteImportant(Properties.INITIAL_WAVE_KNOWN,"INITIAL_WAVE_KNOWN")
    analytics.WriteImportant(Properties.BROKER_TYPE,"BROKER_TYPE")
    analytics.WriteImportant(Properties.READY_COUNT,"READY_COUNT")
    analytics.WriteImportant(Properties.MAX_AVAILABLE_RESOURCES,"MAX_AVAILABLE_RESOURCES")
    analytics.WriteImportant(Properties.CRITICAL_UTILISATION_PERCENT,"CRITICAL_UTILISATION_PERCENT")
    analytics.WriteImportant(Properties.RESOURCE_ADD_NUMBER,"RESOURCE_ADD_NUMBER")
    analytics.WriteImportant(Properties.SET_RASPOREDA,"SET_RASPOREDA")
    analytics.WriteImportant(Properties.RESOURCE_PREPARE_TIME_MEAN,"RESOURCE_PREPARE_TIME_MEAN")
    analytics.WriteImportant(Properties.RESOURCE_PREPARE_TIME_STD,"RESOURCE_PREPARE_TIME_STD")
    analytics.WriteImportant(Properties.USERS_PER_LOGIN_MEAN,"USERS_PER_LOGIN_MEAN")
    analytics.WriteImportant(Properties.NEXT_LOGIN_MEAN,"NEXT_LOGIN_MEAN")
    analytics.WriteImportant(Properties.NEXT_LOGIN_STD,"NEXT_LOGIN_STD")
    analytics.WriteImportant(Properties.USER_COUNT,"USER_COUNT")
    analytics.WriteImportant(user_scheduler.INTER_ARRIVAL_TIMES,"INTER_ARRIVAL_TIMES")
    analytics.WriteImportant(user_scheduler.USERS_NUMBER,"USERS_NUMBER")
    analytics.WriteImportant(user_scheduler.USAGE_TIME,"USAGE_TIME")
    analytics.WriteImportant(user_scheduler.TIME_BETWEEN_LOGINS,"TIME_BETWEEN_LOGINS")

    ## ako je poznato T = 0 i intenzitet inicijalnog udara

    if Properties.INITIAL_WAVE_KNOWN:
        broker.prepare_more_resources(env, user_scheduler.USERS_NUMBER[-1])#dodaje onoliko resursa koliko se korisnika dolazi u prvom talasu


    while len(user_scheduler.INTER_ARRIVAL_TIMES) > 0 and len(user_scheduler.USERS_NUMBER) > 0:

        #print("XXXXXXXXXXXXXXX")
        # unapred kreirati vektor sa vremenma dolaska, zadrzavanja i broja ljudi koji dodju
        next_arrival = user_scheduler.INTER_ARRIVAL_TIMES.pop()
        users_number = user_scheduler.USERS_NUMBER.pop()


        # Wait for the bus
        if ui:
            log.next_arrival(next_arrival)
        yield env.timeout(next_arrival)
        if ui:
            log.arrived(users_number)

        # self.analytics.register_user_login() below is for reporting purposes only
        analytics.log_event(EventType.USER_LOGIN.value, None, env.now, users_number)
        for user in range(users_number):
            user = User("user", user_id)
            user_id += 1
            env.process(broker.user_login(user))

            yield env.timeout(user_scheduler.TIME_BETWEEN_LOGINS.pop())


    analytics.WriteImportant(graph.avg_wait(graph.utilization),"avg_utilization ")#moze i analytics umesto database
    analytics.WriteImportant(graph.avg_wait(graph.wait_for_resource),"avg_wait ")
    analytics.WriteImportant(broker.analytics.SLA1_broke,"SLA1_broke ")
    analytics.WriteImportant(broker.analytics.SLA2_broke,"SLA2_broke ")
    analytics.WriteImportant(broker.analytics.SLA3_broke,"SLA3_broke ")
    analytics.WriteImportant(broker.analytics.SLA4_broke,"SLA4_broke ")
    analytics.WriteImportant("},",None)

    # Prikupljanje parametara (isti redosled kao u zaglavlju CSV-a)
    rezultati = [
        Properties.SIMULATION_UUID,
        Properties.RESOURCE_PREPARE_TIME_MEAN,
        Properties.RESOURCE_PREPARE_TIME_STD,
        Properties.ARRIVAL_PATTERN,
        Properties.BROKER_TYPE,
        Properties.SET_RASPOREDA,
        Properties.USER_COUNT,
        Properties.MAX_AVAILABLE_RESOURCES,
        Properties.CRITICAL_UTILISATION_PERCENT,
        Properties.READY_COUNT,
        Properties.RESOURCE_ADD_NUMBER,
        Properties.INITIAL_WAVE_KNOWN,
        # Prikupljanje izlaznih metrika
        graph.avg_wait(graph.utilization),  # avg_utilization
        graph.avg_wait(graph.wait_for_resource),  # avg_wait
        broker.analytics.SLA1_broke + broker.analytics.SLA2_broke + broker.analytics.SLA3_broke + broker.analytics.SLA4_broke,
        # Ukupno SLA kršenja
        broker.resource_provider.get_resource_count()  # Finalni broj resursa
    ]

    write_results_to_csv(rezultati)  # Poziv nove funkcije

    # ----------------------------------------------------------------------

    env.process(broker.end_process())
    analytics.writeAll()
    analytics.clear_logs()
    print("DONE !!!!!!!!!!!!!!!!!")
    DONE = True
    if ui:
        #blok koji cuva slike
        try:
            output_dir = "simulation_graphs"
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.join(output_dir, f"simulacija_{Properties.SIMULATION_UUID}.png")
            graph.save_plot(filename)
            print(f"Grafik prozora sačuvan kao: {filename}")
        except AttributeError:
            print("Upozorenje: Klasa Graphs nema implementiranu metodu 'save_plot'. Grafik nije sačuvan.")
        except Exception as e:
            print(f"Greška prilikom čuvanja grafika: {e}")

        create_window(broker)#dodala sam broker parametar
        #input()
        #main.destroy()
    #else:
    if _single_run: sys.exit()



def write_results_to_csv(data):
    # Definisanje zaglavlja (Header) CSV fajla
    header = [
        "SIMULATION_UUID",
        "RESOURCE_PREPARE_TIME_MEAN",
        "RESOURCE_PREPARE_TIME_STD",
        "ARRIVAL_PATTERN",
        "BROKER_TYPE",
        "SET_RASPOREDA",
        "USER_COUNT",
        "MAX_AVAILABLE_RESOURCES",
        "CRITICAL_UTILISATION_PERCENT",
        "READY_COUNT",
        "RESOURCE_ADD_NUMBER",
        "INITIAL_WAVE_KNOWN",
        "AVG_UTILIZATION",
        "AVG_WAIT_TIME",
        "TOTAL_SLA_BROKEN",
        "FINAL_RESOURCE_COUNT"
    ]

    # Određivanje da li je potrebno kreirati fajl i upisati zaglavlje
    file_exists = os.path.exists(OUTPUT_CSV_FILE)

    with open(OUTPUT_CSV_FILE, mode='a', newline='') as file: #mod a dodaje u fajl ako on vec postoji
        writer = csv.writer(file)

        # Ako fajl ne postoji, upisujemo zaglavlje
        if not file_exists:
            writer.writerow(header)

        # Upisujemo rezultate trenutne simulacije
        writer.writerow(data)

def create_window(broker):
    if not ui:
        return  # ne prikazuj ništa ako je UI isključen
    t = tk.Toplevel(main)
    t.wm_title("Finished")
    l = tk.Label(t, text=f"Simulation uuid: {Properties.SIMULATION_UUID} \n"
    # f"Total users: {sum(user_scheduler.USERS_NUMBER)} \n"
                         f"Utilization: {broker.analytics.utilization} \n"
                         f"Resource count: {broker.resource_provider.get_resource_count()}\n")
                         #f"SLA brakes: {broker.analytics.SLA_broke}")
    l.pack(side="top", fill="both", expand=True, padx=10, pady=10)

    button = tk.Button(t, text="Close", command=close)
    button.pack(side="top", padx=10, pady=10)


def close():
    main.destroy()


def test_option(opcije):
    global DONE, analytics, user_scheduler, graph, main, canvas, log #,database
    DONE = False
    random.seed(SEED)
    np.random.seed(seed=SEED)
    if not one_important_txt:
        Properties.IMPORTANT_TXT_SUFFIX = json.dumps(opcije)

    print("###$$$$$$$~~~~~~~~~~~~~~~~~~~~~~~~~$$$$$$$###")
    print(f" RESOURCE_PREPARE_TIME_MEAN: {Properties.RESOURCE_PREPARE_TIME_MEAN}")
    print(f" RESOURCE_PREPARE_TIME_STD: {Properties.RESOURCE_PREPARE_TIME_STD}")
    #print(f" SLA: {Properties.SLA}")
    print(f" ARRIVAL_PATTERN: {Properties.ARRIVAL_PATTERN}")
    print(f"BROKER_TYPE: {Properties.BROKER_TYPE}")
    print(f"SET_RASPOREDA: {Properties.SET_RASPOREDA}")
    print(f"INITIAL_WAVE_KNOWN: {Properties.INITIAL_WAVE_KNOWN}")

    #database = DatabaseUtils()
    #database.clear()
    analytics = Analytics()
    analytics.clear_logs()  # Poziv nove metode za čišćenje keša

    env = simpy.rt.RealtimeEnvironment(factor=(5.0 / Properties.TIME_SPEEDUP), strict=False)   # 1.0 faktor moze da se menja da sim napreduje brze/sporije

    analytics = Analytics()

    user_scheduler = UserScheduler()

    user_scheduler.real_mod()
    #database.log_simulation_start()
    analytics.log_simulation_start()

    log = None
    if ui:
        log = DisplayLog(canvas, 5, 20)
    graph = Graphs(canvas, main, analytics.utilization_percent, analytics.waits_for_getting,
                    analytics.arrivals)

    resource_provider = ResourceProvider(env)
    if Properties.BROKER_TYPE == 2:
        broker = BrokerPrepareWhenZero(log, resource_provider, user_scheduler, env)
    elif Properties.BROKER_TYPE == 3:
        broker = BrokerNoPreparing(log, resource_provider, user_scheduler, env)
    else:
        broker = Broker(log, resource_provider, user_scheduler, env)

    process = env.process(start_simulation(env, broker, user_scheduler,opcije))
    env.process(create_clock(env))

    if Properties.CONSTANT_USER_COUNT_ENABLED:
        env.run()
    else:
        env.run(until=Properties.SIMULATION_DURATION_MINUTES)

    if ui:
        main.mainloop()


def start_proc(opcije,ready_count,max_available_resources,critical_utilisation_percent,resource_add_number,user_count, current_seed):
    #time.sleep(0.2)
    #-------------------python sam stavila umesto python3
    #os.system(f"python3 main.py e r_m {opcije[0]} a {opcije[1]} b {opcije[2]} s_r {opcije[3]} i {opcije[4]} r_c {ready_count} m_a_r {max_available_resources} c_u_p {critical_utilisation_percent} r_a_n {resource_add_number}")
    os.system(f"python main.py e r_m {opcije[0]} a {opcije[1]} b {opcije[2]} s_r {opcije[3]} i {opcije[4]} r_c {ready_count} m_a_r {max_available_resources} c_u_p {critical_utilisation_percent} r_a_n {resource_add_number} u_c {user_count} seed {current_seed}")

if _single_run == False:
    # Učitaj sve redove iz CSV-a
    #pomocna promenljiva
    nije_zaustavljeno=True
    all_rows = []
    with open("parametri.csv", newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            all_rows.append(row)

    total_simulations = len(all_rows)
    completed = []
    remaining = list(range(len(all_rows)))

    print(f"Ukupno simulacija za izvršavanje: {total_simulations}")

    while remaining:
        # Pokreni sledecu grupu simulacija
        batch_size = min(Properties.PAUSE_INTERVAL, len(remaining))
        current_batch = remaining[:batch_size]

        for idx in current_batch:
            row = all_rows[idx]

            Properties.RESOURCE_PREPARE_TIME_MEAN = float(row["RESOURCE_PREPARE_TIME_MEAN"])
            Properties.RESOURCE_PREPARE_TIME_STD = Options.RESOURCE_PREPARE_TIME_STD_OPTS
            Properties.ARRIVAL_PATTERN = int(row["ARRIVAL_PATTERN"])
            Properties.BROKER_TYPE = int(row["BROKER_TYPE"])
            Properties.SET_RASPOREDA = int(row["SET_RASPOREDA"])
            Properties.INITIAL_WAVE_KNOWN = row["INITIAL_WAVE"].lower() == "true"

            opcije = [
                Properties.RESOURCE_PREPARE_TIME_MEAN,
                Properties.ARRIVAL_PATTERN,
                Properties.BROKER_TYPE,
                Properties.SET_RASPOREDA,
                Properties.INITIAL_WAVE_KNOWN
            ]
            user_count = Properties.USER_COUNT = int(row["USER_COUNT"])
            max_available_resources = int(row["MAX_AVAILABLE_RESOURCES"])
            critical_utilisation_percent = float(row["CRITICAL_UTILISATION"])
            ready_count = int(row["READY_COUNT"])
            resource_add_number = int(row["RESOURCE_ADD_NUMBER"])

            current_seed = random.randint(1, 100000000)

            print(f"\n{'=' * 60}")
            print(f"Pokretanje simulacije {idx + 1}/{total_simulations}")
            print(f"{'=' * 60}")

            start_proc(opcije, ready_count, max_available_resources,
                       critical_utilisation_percent, resource_add_number, user_count, current_seed)

            completed.append(idx)

        # Ukloni zavrsene iz preostalih
        remaining = remaining[batch_size:]

        # Ako ima jos simulacija
        if remaining:
            print(f"\n{'=' * 70}")
            print(f"Završeno {len(completed)}/{total_simulations} simulacija")
            print(f"Preostalo: {len(remaining)} simulacija")
            print(f"{'=' * 70}")

            while True:
                print("\nOpcije:")
                print(f"1 - Nastavi normalno sa pokretanjem simulacija, odakle je prekinuto")
                print("2 - Pokreni određenu simulaciju")
                print(f"3 - Nastavi sa pokretanjem simulacija od određene simulacije")
                print("4 - Završi sa simulacijama")

                choice = input("\nIzaberite opciju (1/2/3/4): ").strip()

                if choice == '1':
                    print("\nNastavljam sa simulacijama...\n")
                    break
                elif choice == '2':
                    print(f"\nDostupne simulacije: 1-{total_simulations}")
                    print(
                        f"Završene do sada: {[x + 1 for x in sorted(completed)[:10]]}{'...' if len(completed) > 10 else ''}")

                    try:
                        sim_num = int(input("Unesite broj simulacije (1-" + str(total_simulations) + "): "))
                        if 1 <= sim_num <= total_simulations:
                            
                            idx = sim_num - 1
                            row = all_rows[idx]

                            Properties.RESOURCE_PREPARE_TIME_MEAN = float(row["RESOURCE_PREPARE_TIME_MEAN"])
                            Properties.RESOURCE_PREPARE_TIME_STD = Options.RESOURCE_PREPARE_TIME_STD_OPTS
                            Properties.ARRIVAL_PATTERN = int(row["ARRIVAL_PATTERN"])
                            Properties.BROKER_TYPE = int(row["BROKER_TYPE"])
                            Properties.SET_RASPOREDA = int(row["SET_RASPOREDA"])
                            Properties.INITIAL_WAVE_KNOWN = row["INITIAL_WAVE"].lower() == "true"

                            opcije = [
                                Properties.RESOURCE_PREPARE_TIME_MEAN,
                                Properties.ARRIVAL_PATTERN,
                                Properties.BROKER_TYPE,
                                Properties.SET_RASPOREDA,
                                Properties.INITIAL_WAVE_KNOWN
                            ]
                            user_count = Properties.USER_COUNT = int(row["USER_COUNT"])
                            max_available_resources = int(row["MAX_AVAILABLE_RESOURCES"])
                            critical_utilisation_percent = float(row["CRITICAL_UTILISATION"])
                            ready_count = int(row["READY_COUNT"])
                            resource_add_number = int(row["RESOURCE_ADD_NUMBER"])
                            current_seed = random.randint(1, 100000000)
                            print(f"\n{'=' * 60}")
                            print(f"Ponovno pokretanje simulacije {sim_num}")
                            print(f"{'=' * 60}")

                            start_proc(opcije, ready_count, max_available_resources,
                                       critical_utilisation_percent, resource_add_number, user_count, current_seed)

                            print(f"\nSimulacija {sim_num} ponovo izvršena!")
                        else:
                            print("Nevažeći broj simulacije!")
                    except ValueError:
                        print("Molim unesite validan broj!")

                elif choice == '4':
                    print("\nZaustavljanje simulacija...")
                    remaining = []
                    nije_zaustavljeno=False
                    break
                elif choice == '3':
                    try:
                        start_index = int(input("Unesite broj simulacije od koje želite da nastavite: ")) - 1
                        if 0 <= start_index < total_simulations:
                            remaining = list(range(start_index, total_simulations))
                            print(
                                f"\nNastavljam sledećih {min(Properties.PAUSE_INTERVAL, len(remaining))} simulacija od {start_index + 1}-te...\n")
                            break
                        else:
                            print("Nevažeći broj simulacije!")
                    except ValueError:
                        print("Molim unesite validan broj!")
                else:
                    print("Nevažeća opcija! Unesite 1, 2, 3 ili 4.")

    print(f"\n{'=' * 70}")
    print(f"SVE SIMULACIJE ZAVRŠENE!")
    print(f"Ukupno izvršeno: {len(completed)}/{total_simulations}")
    print(f"{'=' * 70}")

    # kad se zavrse sve korisnik moze da pokrene odredjenu ili da zatvori program
    while nije_zaustavljeno: #True:
        print("\nSve simulacije su završene.")
        print("Opcije:")
        print("1 - Pokreni ponovo određenu simulaciju")
        print("2 - Završi program")

        post_choice = input("\nIzaberite opciju (1/2): ").strip()

        if post_choice == '1':
            print(f"\nDostupne simulacije: 1-{total_simulations}")
            try:
                sim_num = int(input("Unesite broj simulacije koju želite da pokrenete ponovo: "))
                if 1 <= sim_num <= total_simulations:
                    idx = sim_num - 1
                    row = all_rows[idx]

                    Properties.RESOURCE_PREPARE_TIME_MEAN = float(row["RESOURCE_PREPARE_TIME_MEAN"])
                    Properties.RESOURCE_PREPARE_TIME_STD = Options.RESOURCE_PREPARE_TIME_STD_OPTS
                    Properties.ARRIVAL_PATTERN = int(row["ARRIVAL_PATTERN"])
                    Properties.BROKER_TYPE = int(row["BROKER_TYPE"])
                    Properties.SET_RASPOREDA = int(row["SET_RASPOREDA"])
                    Properties.INITIAL_WAVE_KNOWN = row["INITIAL_WAVE"].lower() == "true"

                    opcije = [
                        Properties.RESOURCE_PREPARE_TIME_MEAN,
                        Properties.ARRIVAL_PATTERN,
                        Properties.BROKER_TYPE,
                        Properties.SET_RASPOREDA,
                        Properties.INITIAL_WAVE_KNOWN
                    ]
                    user_count = Properties.USER_COUNT = int(row["USER_COUNT"])
                    max_available_resources = int(row["MAX_AVAILABLE_RESOURCES"])
                    critical_utilisation_percent = float(row["CRITICAL_UTILISATION"])
                    ready_count = int(row["READY_COUNT"])
                    resource_add_number = int(row["RESOURCE_ADD_NUMBER"])
                    current_seed = random.randint(1, 100000000)
                    print(f"\n{'=' * 60}")
                    print(f"Ponovno pokretanje simulacije {sim_num}")
                    print(f"{'=' * 60}")

                    start_proc(opcije, ready_count, max_available_resources,
                               critical_utilisation_percent, resource_add_number, user_count, current_seed)

                    print(f"\nSimulacija {sim_num} ponovo izvršena!\n")

                else:
                    print("Nevažeći broj simulacije!")
            except ValueError:
                print("Unesite validan broj!")

        elif post_choice == '2':
            print("\nProgram je završen.")
            break
        else:
            print("Nevažeća opcija! Unesite 1 ili 2.")

else:
    if _resurs_mean is None:
        _resurs_mean = Options.RESOURCE_PREPARE_TIME_MEAN_OPTS[0]
    if _resurs_std is None:
        _resurs_std = Options.RESOURCE_PREPARE_TIME_STD_OPTS
    if _arrival_pattern is None:
        _arrival_pattern = Properties.ARRIVAL_PATTERN
    if _broker_choice is None:
        _broker_choice = Properties.BROKER_TYPE
    if _set_raspodela is None:
        _set_raspodela = Properties.SET_RASPOREDA
        if _set_raspodela == -1:
            _set_raspodela = 0

    if _initial_wave is None:
        _initial_wave = Properties.INITIAL_WAVE_KNOWN

    opcije = [_resurs_mean, _arrival_pattern, _broker_choice, _set_raspodela, _initial_wave]
    Properties.RESOURCE_PREPARE_TIME_MEAN = _resurs_mean
    Properties.RESOURCE_PREPARE_TIME_STD = _resurs_std
    # Properties.SLA = _sla
    Properties.ARRIVAL_PATTERN = _arrival_pattern
    Properties.BROKER_TYPE = _broker_choice
    Properties.SET_RASPOREDA = _set_raspodela
    Properties.INITIAL_WAVE_KNOWN = _initial_wave

    test_option(opcije)






