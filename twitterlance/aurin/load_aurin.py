#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, os
from couchdb import couch
from django.conf import settings

def getDeath(city):
    aurinpath = os.path.join(settings.STATICFILES_DIRS[0], 'aurin')
    with open(f"{aurinpath}/deathrate.json", 'r', encoding='utf-8') as f:
        death = json.load(f)
    for each in death["features"]:
        if each["properties"]['gcc_name16'] == city:
            deathRate = each["properties"]['_2019_std_death_rate']
    return deathRate

def getMales(city):
    aurinpath = os.path.join(settings.STATICFILES_DIRS[0], 'aurin')
    with open(f"{aurinpath}/byGender.json", 'r', encoding='utf-8') as f:
        gender = json.load(f)
    for each in gender["features"]:
        if each["properties"]['gcc_name16'] == city:
            males = each["properties"]['tot_m']
            persons = each["properties"]['tot_p']
            male_percent = round(males/persons, 2)
    return male_percent,persons

def getUnemployment(city):
    aurinpath = os.path.join(settings.STATICFILES_DIRS[0], 'aurin')
    with open(f"{aurinpath}/unemployment.json", 'r', encoding='utf-8') as f:
        unemployment = json.load(f)
    for each in unemployment["features"]:
        if each["properties"]['gcc_name16'] == city:
            unemployment = each["properties"]['percent_unemployment_p'] 
    
    return unemployment

def getAgeIncome(city):
    aurinpath = os.path.join(settings.STATICFILES_DIRS[0], 'aurin')
    with open(f"{aurinpath}/ageandincome.json", 'r', encoding='utf-8') as f:
        AgeIncome = json.load(f)
    for each in AgeIncome["features"]:
        if each["properties"]['gcc_name16'] == city:
            age = each["properties"]['median_age_persons'] 
            income = each["properties"]['median_tot_prsnl_inc_weekly']
    return age, income

def getHousingPrice(city):
    aurinpath = os.path.join(settings.STATICFILES_DIRS[0], 'aurin')
    with open(f"{aurinpath}/housingprice.json", 'r', encoding='utf-8') as f:
        housingPrice = json.load(f)
    for each in housingPrice["features"]:
        if each["properties"]['gcc'] == city:
            price = int(each["properties"]['median_sales_price_last_12_months'])        
    return price

def getEducation(city):
    aurinpath = os.path.join(settings.STATICFILES_DIRS[0], 'aurin')
    with open(f"{aurinpath}/educationlevel.json", 'r', encoding='utf-8') as f:
        housingPrice = json.load(f)
    for each in housingPrice["features"]:
        if each["properties"]['gcc_name16'] == city:
             postgraduate = int(each["properties"]["p_tot_tot_pgde_gddp_gdctl"])
             advance =  int(each["properties"]["p_tot_tot_adip_dipl"])
             certificate = int(each["properties"]["p_tot_tot_ct_i_ii"])+int(each["properties"]["p_tot_tot_ct_iii_and_iv_l"])
             bachelor = int(each["properties"]["p_tot_tot_bdl"])
             education= {"postgraduate":postgraduate,"bachelor":bachelor,"advance":advance,"certificate":certificate}
             
    return education

def load_data():
    cities=["Greater Melbourne","Greater Sydney","Greater Adelaide","Australian Capital Territory","Greater Brisbane","Greater Perth"]
    cities_profile = {}
    print('Loading aurin data to CouchDB')
    for city in cities:
        cities_profile[city]={}
        cities_profile[city]["death rate"] = getDeath(city)
        cities_profile[city]["male%"],population = getMales(city)
        cities_profile[city]["unemployment"] = getUnemployment(city)
        cities_profile[city]["age"],cities_profile[city]["income"]=getAgeIncome(city)
        cities_profile[city]["housing price"] = getHousingPrice(city)
        cities_profile[city]["education_level"] = getEducation(city)
        edu = getEducation(city)
        total = 0
        for k, v in edu.items():
            total += v
        for k, v in edu.items():
            edu[k] = round( v / total, 2)
        cities_profile[city]["education"] = edu

            
    for key, value in cities_profile.items(): 
        couch.put(f'aurin/{key}', {'_id': key, 'features': value})

