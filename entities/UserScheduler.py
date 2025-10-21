import csv
import os
import random
import numpy as np
import math

from scipy import stats
from utils.Proprerties import Properties
from statsmodels.distributions.mixture_rvs import MixtureDistribution


class UserScheduler:
    def __init__(self):
        self.INTER_ARRIVAL_TIMES = []  # Vremenski razmaci između dolazaka grupa korisnika
        self.USERS_NUMBER = [] #Broj korisnika koji dolaze u određenom trenutku (tj. br. korisnika u grupi)
        self.USAGE_TIME = [] # Vreme korišćenja za svakog korisnika.
        self.TIME_BETWEEN_LOGINS = [] #Vremenski razmaci između prijava unutar grupe.

        '''self.values = [4.5772, 0.1835,
                       2.7327, 0.586,
                       5.1684, 2.2204,
                       9.5069, 2.4728]
        self.prob = [0.6724, 0.1137, 0.1345, 0.0794]'''

        self.mixdis = MixtureDistribution() #Kreira se instanca klase MixtureDistribution za rad sa distribucijama


    # stari kod, ne koristi se ovaj mod
    """def basic_mod(self):
        self.INTER_ARRIVAL_TIMES = [random.expovariate(1 / Properties.NEXT_LOGIN_MEAN)
                                    for _ in range(80)]
        self.USERS_NUMBER = [Properties.get_positive_value_gauss(Properties.USERS_PER_LOGIN_MEAN,
                                                                 Properties.USERS_PER_LOGIN_STD)
                             for _ in range(80)]
        self.USAGE_TIME = [Properties.get_positive_value_gauss(Properties.USERS_PER_LOGIN_MEAN,
                                                               Properties.USERS_PER_LOGIN_STD)
                           for _ in range(sum(self.USERS_NUMBER))]
"""

#raspored dolazaka korisnika:
    def real_mod(self):
        # inter arrival times
        print("POZVAN real_mod()")
        if Properties.CONSTANT_USER_COUNT_ENABLED:#fiksan br. ukupnih korisnika
                                                                                                   #umesto provere da li promenljive CONSTANT_USER_COUNT_ENABLED uvek se izvrsava ovaj kod tj uvek se koristi const vrednost za br korisnika
            self.USERS_NUMBER = []
            total_users_count = Properties.USER_COUNT

            if Properties.ARRIVAL_PATTERN == 2:       ## inicijalni udar     ---- arrival pattern 1 i 2 overvrajtuju vredn iz properties

                #veca vredn za 1. talas korisnika (veliki pocetni talas)
                Properties.USERS_PER_LOGIN_MEAN = random.choice((20, 35, 100))#random.choice - bira jednu od tih vrednosti
                Properties.NEXT_LOGIN_MEAN = 0                                ### next login mean/std - za racunanje posle koliko dolazi sld grupa
                Properties.NEXT_LOGIN_STD = 0

                user_count = Properties.get_positive_value_gauss(Properties.USERS_PER_LOGIN_MEAN,
                                                                 Properties.USERS_PER_LOGIN_STD)
                if user_count > total_users_count: # ako je br. korisnika u 1. grupi veci od uk br. korinika
                    user_count = total_users_count


                self.USERS_NUMBER.append(user_count)
                total_users_count -= user_count

                #ostale grupe su manje od 1. (1. je 20-100) (ost su 3-8)
                Properties.USERS_PER_LOGIN_MEAN = random.choice((3, 5, 8))
                Properties.NEXT_LOGIN_MEAN = random.choice((15, 30))
                Properties.NEXT_LOGIN_STD = 3

            elif Properties.ARRIVAL_PATTERN == 1:#ravnomerni dolasci
                Properties.NEXT_LOGIN_MEAN = random.choice((90, 120))
                Properties.USERS_PER_LOGIN_MEAN = random.choice((20, 35))


            while total_users_count > 0:#petlja se ponavlja dokle god ima korisnika
                user_count = Properties.get_positive_value_gauss(Properties.USERS_PER_LOGIN_MEAN,
                                                                 Properties.USERS_PER_LOGIN_STD)
                if user_count>total_users_count:
                    user_count = total_users_count

                self.USERS_NUMBER.append(user_count)
                total_users_count -= user_count

        else:#ako nemamo fiksan br. korisnika - parivmo 80 grupa
            self.USERS_NUMBER = [Properties.get_positive_value_gauss(Properties.USERS_PER_LOGIN_MEAN,
                                                                     Properties.USERS_PER_LOGIN_STD)
                                 for _ in range(80)]

        # pattern 3 je van gornjeg if jer ne zavisi od toga da li je podeseno da je broj korisnika konstantan
        # 1 i 2 manjaju parametre za generisanje grupa pa se dobija iz njih inter_arrival_times, 3 cita inter_arrival_times iz csv fajla
        if Properties.ARRIVAL_PATTERN == 3:
            csv_file_path = os.path.join("LOGS", "random_numbers.csv")
            print(f"Putanja do fajla: {os.path.abspath(csv_file_path)}")
            print(f"Trenutni radni direktorijum: {os.getcwd()}")

            def option3_generate_numbers():
                random_numbers = [random.randint(20, 120) for _ in range(sum(self.USERS_NUMBER))]#users_num ima listu brojeva korisnika u svakoj grupi,
                #sorted_numbers = sorted(random_numbers)
                with open(csv_file_path, mode='w', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerows(map(lambda x: [x], random_numbers))

            option3_generate_numbers()
            with open(csv_file_path, "r") as csvfile:
                csv_reader = csv.reader(csvfile)
                self.INTER_ARRIVAL_TIMES = [int(row[0]) for row in csv_reader]
        # ako nije selektovan 3 onda se dobija na osn vrednosti koje su pattern 1 ili 2 promenili
        else:
            self.INTER_ARRIVAL_TIMES = [Properties.get_positive_value_gauss(Properties.NEXT_LOGIN_MEAN,
                                                                        Properties.NEXT_LOGIN_STD)
                                        for _ in range(sum(self.USERS_NUMBER))]


        '''self.USAGE_TIME = [np.random.gamma(Properties.GAMMA_25_SHAPE, Properties.GAMMA_25_SCALE)
                           for _ in range(math.ceil(sum(self.USERS_NUMBER) * 0.25))]
        self.USAGE_TIME.extend([np.random.gamma(Properties.GAMMA_75_SHAPE, Properties.GAMMA_75_SCALE)
                                for _ in range(math.ceil(sum(self.USERS_NUMBER) * 0.75))])

        self.USAGE_TIME = [(x * 268) + Properties.MINIMUM_USAGE_TIME for x in self.USAGE_TIME]'''

        #####za mesanje vrednosti
        def getSet(setIdx):#za mixdis klasu priprema parametre za generisanje mesovite distribucije
            ##"set","weight","distribution","alpha","beta"
            xlsx = [#lista tuplova 1. el tupla je ime 2. j
                ("duration_C1_N", [
                    (0.6724, "Lognormal", 4.5772, 0.1835),#vrv da ce da bude izabrana ta distribucija, distribucija, 1. i 2. parametar distribucije
                    (0.1137, "Weibull", 2.7327, 0.586),
                    (0.1345, "Normal", 5.1684, 2.2204),
                    (0.0794, "Normal", 9.5069, 2.4728)]),
                ("duration_C1_pc_D", [
                    (0.1985, "Lognormal", 2.1667, 0.2421),
                    (0.4922, "Weibull", 4.54, 0.3426),
                    (0.2982, "Weibull", 4.9432, 0.3223),
                    (0.0015, "Normal", 5.09E-13, 1.00E-08),
                    (0.0096, "Normal", 1.6392, 1.3063)]),
                ("duration_C2_N", [
                    (0.2254, "Lognormal", 2.4633, 0.2729),
                    (0.7746, "Normal", 158.26, 2435.91)]),
                ("duration_C2_pc_D", [
                    (0.5483, "Lognormal", 2.224, 0.2871),
                    (0.4517, "Weibull", 4.9303, 0.4792)]),
                ("duration_C4_N", [
                    (0.2369, "Weibull", 4.5073, 0.0576),
                    (0.6087, "Weibull", 4.2193, 0.1981),
                    (0.1544, "Weibull", 2.7446, 0.6235)]),
                ("duration_C4_pc_D", [
                    (0.0156, "Weibull", -1.2222, 0.6612),
                    (0.7057, "Weibull", 4.4412, 0.1878),
                    (0.1999, "Weibull", 3.7023, 0.5288),
                    (0.0788, "_", 0, 0)]),
                ("duration_C1_1_N", [
                    (0.2445, "Weibull", 2.3179, 0.3894),
                    (0.3329, "Weibull", 4.6501, 0.1962),
                    (0.4226, "Weibull", 4.6419, 0.44)]),
                ("duration_C1_3_N", [
                    (0.2879, "Lognormal", 1.9648, 0.2977),
                    (0.7121, "Weibull", 4.7319, 0.3754)]),
                ("duration_C1_4_N", [
                    (0.3202, "Weibull", 2.0401, 0.3978),
                    (0.6798, "Weibull", 4.8025, 0.527)])
            ]
            modeli = dict(Lognormal = stats.lognorm,Weibull = stats.weibull_min,_ = stats.norm,Normal = stats.norm) #mapiranje između tekstualnih imena distribucija (koja se nalaze u xlsx listi) i stvarnih, matematičkih objekata distribucije iz naučne Python biblioteke

            def model2dict(tupl):#kreira recnik da bi znao koju mat fju da pozove
                m = tupl[1][0].lower()
                if m == "n" or m == "_":
                    return dict(loc=tupl[2], scale=np.sqrt(tupl[3]))
                if m == "l":
                    return dict(loc=0, scale=np.exp(tupl[2]), args=(np.sqrt(tupl[3]),))
                if m == "w":
                    return dict(loc=0, scale=np.exp(tupl[2]), args=(1.0 / tupl[3],))

            set_ = xlsx[setIdx][1]
            return dict(
                prob=list(map(lambda x: x[0], set_)),
                size=math.ceil(sum(self.USERS_NUMBER)),
                dist=list(map(lambda x: modeli[x[1]], set_)),
                kwargs=tuple(map(model2dict, set_))
            )
        ##Properties.SET_RASPOREDA=random.choice((0,1,2,3,4,5,6,7,8))
        self.USAGE_TIME = self.mixdis.rvs(**getSet(Properties.SET_RASPOREDA))

        self.USAGE_TIME = [abs(x) + Properties.MINIMUM_USAGE_TIME for x in self.USAGE_TIME]
        # povecati svaki za neku vrednost
        self.TIME_BETWEEN_LOGINS = [random.expovariate(Properties.EXPONENTIAL_LAMBDA) + 1
                                    for _ in range(sum(self.USERS_NUMBER))]

        if Properties.ARRIVAL_PATTERN == 2:
            self.USERS_NUMBER.reverse()
            random.shuffle(self.INTER_ARRIVAL_TIMES[1:])
            random.shuffle(self.USERS_NUMBER[1:])
            random.shuffle(self.USAGE_TIME[1:])
            random.shuffle(self.TIME_BETWEEN_LOGINS[1:])

        else:
            random.shuffle(self.INTER_ARRIVAL_TIMES)
            random.shuffle(self.USERS_NUMBER)
            random.shuffle(self.USAGE_TIME)
            random.shuffle(self.TIME_BETWEEN_LOGINS)
        
        # print("#####################################")
        # print(self.INTER_ARRIVAL_TIMES)
        # print(self.USERS_NUMBER)
        # print(self.USAGE_TIME)
        # print(self.TIME_BETWEEN_LOGINS)
        # print("#####################################")

    def examination_date_mod(self):#ovo se ne poziva nigde
        # inter arrival times
        self.INTER_ARRIVAL_TIMES = [Properties.get_positive_value_gauss(Properties.NEXT_LOGIN_MEAN,
                                                                        Properties.NEXT_LOGIN_STD)
                                    for _ in range(80)]
        self.USERS_NUMBER = [Properties.get_positive_value_gauss(Properties.USERS_PER_LOGIN_MEAN,
                                                                 Properties.USERS_PER_LOGIN_STD) + 1
                             for _ in range(80)]

        self.USAGE_TIME = [np.random.gamma(Properties.GAMMA_25_SHAPE, Properties.GAMMA_25_SCALE)
                           for _ in range(math.ceil(sum(self.USERS_NUMBER) * 0.25))]
        self.USAGE_TIME.extend([np.random.gamma(Properties.GAMMA_75_SHAPE, Properties.GAMMA_75_SCALE)
                                for _ in range(math.ceil(sum(self.USERS_NUMBER) * 0.75))])

        self.USAGE_TIME = [(x * 268) + 20 for x in self.USAGE_TIME]

        # povecati svaki za neku vrednost
        self.TIME_BETWEEN_LOGINS = [random.expovariate(5 / 3) + 1 for _ in range(sum(self.USERS_NUMBER))]
        # self.TIME_BETWEEN_LOGINS = [x+3 for x in self.TIME_BETWEEN_LOGINS]

        random.shuffle(self.INTER_ARRIVAL_TIMES)
        random.shuffle(self.USERS_NUMBER)
        random.shuffle(self.USAGE_TIME)
        random.shuffle(self.TIME_BETWEEN_LOGINS)
