import inspect
import random
from builtins import staticmethod


class Properties:
    SIMULATION_UUID = 0
    TIME_SPEEDUP = 2000000
    SIMULATION_DURATION_MINUTES = 200

    PAUSE_INTERVAL=2# 999999999 #posle koliko simulacija se korisnik pita da li da nastavi dalje da pokrece simulacije

    CONSTANT_USER_COUNT_ENABLED = True
    USER_COUNT = 50

    NEXT_LOGIN_MEAN = 5
    NEXT_LOGIN_STD = 3

    USERS_PER_LOGIN_MEAN = 20
    USERS_PER_LOGIN_STD = 3

    SET_RASPOREDA = -1

    ####### Sledeca 4 mi optimizujemo (menjamo):
    READY_COUNT = 10                                          # koliko resursa spremno na startu
    MAX_AVAILABLE_RESOURCES = 150                               # koliko max imamo resursa available
    CRITICAL_UTILISATION_PERCENT =0.6                                # kada da sprema nove resurse
    RESOURCE_ADD_NUMBER = 1                                         # ovoliko resursa se dodaju kad critical util
    #RESOURCE_ADD_RATE = 3   # ovo se ne koristi nigde

    NUMBER_OF_WORKERS = 3

    RESOURCE_USAGE_TIME_MEAN = 60
    RESOURCE_USAGE_TIME_STD = 5#15

    RESOURCE_PREPARE_TIME_MEAN = 2#5
    RESOURCE_PREPARE_TIME_STD = 1#2

    # GAMMA_25_SHAPE = 0.181
    # GAMMA_25_SCALE = 0.56
    # GAMMA_75_SHAPE = 0.36
    # GAMMA_75_SCALE = 0.12

    EXPONENTIAL_LAMBDA = 5/3

    MINIMUM_USAGE_TIME = 0

    ##MINIMUM_USAGE_TIME = 20


    # GAMMA_25_SHAPE = 7.5
    # GAMMA_25_SCALE = 0.56
    # GAMMA_75_SHAPE = 0.36
    # GAMMA_75_SCALE = 0.12

    SLA1 = 0.1
    SLA2 = 0.5
    SLA3 = 1.0
    SLA4 = 1.5
    ARRIVAL_PATTERN = 3
    INITIAL_WAVE_KNOWN = True
    BROKER_TYPE = 1

    IMPORTANT_TXT_SUFFIX = ""

    @staticmethod
    def get_positive_value_gauss(mean, std):
        value = int(random.gauss(mean, std))
        if value < 0:
            value = 1
        return value

    @classmethod
    def get_next_users_number(cls):
        value = int(random.gauss(cls.USERS_PER_LOGIN_MEAN, cls.USERS_PER_LOGIN_STD))
        if value < 0:
            value = 1
        return value

    @classmethod
    def get_parameters(cls):
        attributes = inspect.getmembers(Properties, lambda a: not (inspect.isroutine(a)))
        return [a for a in attributes if not (a[0].startswith('__')
                                              or a[0].endswith('__')
                                              or a[0].startswith('SIMULATION')
                                              or a[0].startswith('TIME_SPEEDUP')
                                              or a[0].startswith('SIMULATION_DURATION_MINUTES'))]
