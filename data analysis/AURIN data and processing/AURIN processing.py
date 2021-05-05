#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
cities=["Greater Melbourne","Greater Sydney","Greater Adelaide","Australian Capital Territory"]

def getDeath(city):
    with open("death rate.json", 'r', encoding='utf-8') as f:
        death = json.load(f)
    for each in death["features"]:
        if each["properties"]['gcc_name16'] == city:
            deathRate = each["properties"]['_2019_std_death_rate']
    return deathRate

def getMales(city):
    with open("byGender.json", 'r', encoding='utf-8') as f:
        gender = json.load(f)
    for each in gender["features"]:
        if each["properties"]['gcc_name16'] == city:
            males = each["properties"]['tot_m']
            persons = each["properties"]['tot_p']
            male_percent = round(males/persons, 2)
    return male_percent,persons

def getUnemployment(city):
    with open("unemployment.json", 'r', encoding='utf-8') as f:
        unemployment = json.load(f)
    for each in unemployment["features"]:
        if each["properties"]['gcc_name16'] == city:
            unemployment = each["properties"]['percent_unemployment_p'] 
    
    return unemployment

def getAgeIncome(city):
    with open("age and income.json", 'r', encoding='utf-8') as f:
        AgeIncome = json.load(f)
    for each in AgeIncome["features"]:
        if each["properties"]['gcc_name16'] == city:
            age = each["properties"]['median_age_persons'] 
            income = each["properties"]['median_tot_prsnl_inc_weekly']
    return age, income

def getHousingPrice(city):
    with open("housing price.json", 'r', encoding='utf-8') as f:
        housingPrice = json.load(f)
    for each in housingPrice["features"]:
        if each["properties"]['gcc'] == city:
            price = int(each["properties"]['median_sales_price_last_12_months'])        
    return price

def getEducation(city):
    with open("educatiion level.json", 'r', encoding='utf-8') as f:
        housingPrice = json.load(f)
    for each in housingPrice["features"]:
        if each["properties"]['gcc_name16'] == city:
             educated = int(each["properties"]['p_tot_tot_tot'])
    return educated

cities=["Greater Melbourne","Greater Sydney","Greater Adelaide","Australian Capital Territory"]
cities_profile = {}
        
for city in cities:
        cities_profile[city]={}
        cities_profile[city]["death rate"] = getDeath(city)
        cities_profile[city]["male%"],population = getMales(city)
        cities_profile[city]["unemployment"] = getUnemployment(city)
        cities_profile[city]["age"],cities_profile[city]["income"]=getAgeIncome(city)
        cities_profile[city]["housing price"] = getHousingPrice(city)
        educated = getEducation(city)
        cities_profile[city]["educated%"] = round(educated/population,2)
        
cities_profile  

#with open('citiesProfile.json', 'w') as f:
#    for value in cities_profile.items():
#        print(json.dumps(value, sort_keys=True)) 
#        f.write(json.dumps(value, sort_keys=True, indent=0))
#        f.write('\n')

with open('cities profile.json', 'w') as json_file:
  json.dump(cities_profile, json_file)