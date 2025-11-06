import json
import numpy as np
from matplotlib.contour import ContourSet

with open('mergedFiltered2.txt', 'r', encoding='utf-8') as f:
    content = f.read().strip()
if content.endswith(','):
    content = content[:-1]
content = '[' + content + ']'
with open('mergedOutput.txt', 'w', encoding='utf-8') as f:
    f.write(content)

f = open('mergedOutput.txt')#mergedFiltered2.txt

svi = json.load(f)
poOpcijama = dict()
poParametrima = dict()
poParametrima2 = dict()
print(len(svi))

for i in svi:
    ####ZA BROKER
    #if(i["BROKER_TYPE"] != 3): continue#preskace sve koji nemaju tu vrednost za broker
    ###############
    #####ZA SET RASPOREDA:

    if "opcije" not in i:#or not isinstance(i["opcije"], (list, tuple)) or len(i["opcije"]) <= 4
        continue  # preskače ako opcije ne postoje

    if isinstance(i["opcije"], str):
        i["opcije"] = json.loads(i["opcije"].replace("True", "true").replace("False", "false"))

    if i["opcije"][3] != 0:#set rasp je 4. vredn u opcijama, analiziramo 0,2,4
        continue  # preskače ako peta vrednost nije 0

    if isinstance(i["opcije"], list):
        i["opcije"] = json.dumps(i["opcije"])

    ############################################################

    opcije_key = tuple(i["opcije"]) if isinstance(i["opcije"], list) else i["opcije"]
    ###

    if not (i["opcije"] in poOpcijama):
        poOpcijama[i["opcije"]] = []
    parametriStr = f'{i["READY_COUNT"]}-{i["MAX_AVAILABLE_RESOURCES"]}-{i["CRITICAL_UTILISATION_PERCENT"]}-{i["RESOURCE_ADD_NUMBER"]}'
    if not (parametriStr in poParametrima):
        poParametrima[parametriStr] = []
        poParametrima2[parametriStr] = dict()#dict(score1=0,score2=0,scoreG=0,wait=0,util=0,sla1=0,sla2=0,sla3=0,sla4=0)
    score1 = 0
    score2 = -i["MAX_AVAILABLE_RESOURCES"]
    scoreG = i["avg_utilization"] - i["avg_wait"]*40
    ut = 0
    if "USAGE_TIME" in i:
        for u in json.loads(i["USAGE_TIME"]):
            ut += u
    else:
        ut = 0
    score1 = -(ut / (i["avg_utilization"]/100.0)) / 109.0
    i["score1"] = scoreG * 0.1 + 0.9 * (score1)
    i["score2"] = score2 *0.9 + scoreG * 0.1
    i["scoreG"] = scoreG * 0.01 - i["SLA1_broke"]
    poParametrima2[parametriStr]["id"] = parametriStr
    # xxx = f'{i["scoreG"]}-{i["score1"]}-{i["score2"]}'
    # if("last" in poParametrima2[parametriStr] and poParametrima2[parametriStr]["last"] != xxx):
    #     print("NIJE ISTO")
    #     print(xxx)
    #     print(poParametrima2[parametriStr]["last"])
    #     input()
    # poParametrima2[parametriStr]["last"] = xxx
    poParametrima[parametriStr].append(i)

    #Promenila sam ovo:
    #poOpcijama[i["opcije"]].append(i)
    poOpcijama[opcije_key].append(i)


for v in poParametrima2:
    # poParametrima2[v]["score1"] = np.mean(list(map(lambda x: x["score1"],poParametrima[v])))
    # poParametrima2[v]["score2"] = np.mean(list(map(lambda x: x["score2"],poParametrima[v])))
    # poParametrima2[v]["scoreG"] = np.mean(list(map(lambda x: x["scoreG"],poParametrima[v])))
    for p in ["score1", "score2", "scoreG","avg_utilization","avg_wait", "SLA1_broke","SLA2_broke","SLA3_broke","SLA4_broke"]:
        poParametrima2[v][p] = "\t"+("  %.2f" % np.mean(list(map(lambda x: x[p],poParametrima[v]))))
        #poParametrima2[v][p] = np.mean(list(map(lambda x: x[p],poParametrima[v])))
    
    for p in ["SLA1_broke","SLA2_broke","SLA3_broke","SLA4_broke","avg_wait","avg_utilization"]:
        prf = "    "
        if p=="avg_utilization":
            prf = " %"
        if p=="avg_wait":
            prf=" min"
        poParametrima2[v][p] += f'{prf}   \tmax: {np.max(list(map(lambda x: x[p],poParametrima[v]))):.2f}{prf}'
        poParametrima2[v][p] += f'\tmin: {np.min(list(map(lambda x: x[p],poParametrima[v]))):.2f}{prf}'
    
def printSlucaj(i,f):
    f.write("\n@@@@@@@@@@@@@@")
    f.write("\n") 
    s = i[0]
    parametriStr = f'{s["READY_COUNT"]}-{s["MAX_AVAILABLE_RESOURCES"]}-{s["CRITICAL_UTILISATION_PERCENT"]}-{s["RESOURCE_ADD_NUMBER"]}'
    f.write(f'RC: {s["READY_COUNT"]} , max: {s["MAX_AVAILABLE_RESOURCES"]} , crit: {s["CRITICAL_UTILISATION_PERCENT"]} , add: {s["RESOURCE_ADD_NUMBER"]}')
    f.write("\n") 
    for p in poParametrima2[parametriStr]:
        f.write(f'\t{p.replace("avg_utilization","avg_util").replace("SLA1_broke","SLA 0.1").replace("SLA2_broke","SLA 0.5").replace("SLA3_broke","SLA 1.0").replace("SLA4_broke","SLA 1.5")}:{poParametrima2[parametriStr][p]}')
        f.write("\n")
        if(p=="scoreG"): f.write("\n")
        if(p=="avg_wait"): f.write("\n")
"""
    # print(f'')
    # print(f'score1: {poParametrima2[parametriStr]["score1"]}')
    # print(f'score2: {poParametrima2[parametriStr]["score2"]}')
    # print(f'scoreG: {poParametrima2[parametriStr]["scoreG"]}')
    # print(f'wait: {poParametrima2[parametriStr]["wait"]}')
    # print(f'util: {poParametrima2[parametriStr]["util"]}')
    # print(f'sla1: {poParametrima2[parametriStr]["sla1"]}')
    # print(f'sla2: {poParametrima2[parametriStr]["sla2"]}')
    # print(f'sla3: {poParametrima2[parametriStr]["sla3"]}')
    # print(f'sla4: {poParametrima2[parametriStr]["sla4"]}')

    # if(s["score1"]):
    #     print(f'score1: {s["score1"]}')
    # if(s["score2"]):
    #     print(f'score2: {s["score2"]}')
    # if(s["scoreG"]):
    #     print(f'scoreG: {s["scoreG"]}')
    
    # for s in i:
    #     print("~~~~~~~~~~~~~~~")
    #     print(f'util: {s["avg_utilization"]}')
    #     print(f'wait: {s["avg_wait"]}')
    #     print(f'sla1: {s["SLA1_broke"]}')
    #     print(f'sla2: {s["SLA2_broke"]}')
    #     print(f'sla3: {s["SLA3_broke"]}')
    #     print(f'sla4: {s["SLA4_broke"]}')
"""
#for v in poParametrima2:
#print(v)
skr = "SLA1_broke"
    
sortirano = list(sorted(poParametrima2.values(),key=lambda x: np.mean(list(map(lambda y: y["scoreG"],poParametrima[x['id']]))),reverse=True))
f = open(f"{skr}.txt", "w")
#print("#######################")
for i in sortirano:#[:40]:
    printSlucaj(poParametrima[i["id"]],f)
    #printSlucaj(poParametrima[i["id"]])
# f.write("----------------------")
# f.write("\n") 
# for i in sortirano[-40:]:
#     printSlucaj(poParametrima[i["id"]],f)
#     #printSlucaj(poParametrima[i["id"]])
# #f.write("Now the file has more content!")
f.close()
