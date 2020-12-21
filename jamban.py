#!/usr/bin/python3
import csv
import subprocess
import os
import re
import argparse
import sys
from argparse import RawTextHelpFormatter

def getTimeOut(action):
    if action == 'add':
        timeOut = " timeout " + args.timeout
    else:
        timeOut = ''
    return timeOut

def clientAction(client, action):
    cmd = "sudo nft " + action + " element " + args.banset + " { " + client + getTimeOut(action) + " }"
    errno = subprocess.call(cmd, shell=True)
    if (errno == 0):
        print("Action <" + action + "> on " + client + " was successful")
    else:
        print("Action <" + action + "> on " + client + " failed")

def unbanAll(clients):
    for IP in clients:
        clientAction(clients[IP][1], 'delete')

def getBannedIPs():
    i=0
    clientDict={}
    cmd = "sudo nft list set " + args.banset
    cmdOutput = subprocess.getoutput(cmd)
    IPs = re.findall(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b', cmdOutput)
    for x in IPs:
        i+=1
        clientDict.update({ i: [ '', x ] })
    return clientDict

def selection(clients):
    valid_range=len(clients)
    try:
        choice = int(input("Select entry (1 - " + str(valid_range) + ") or any other character to abort: "))
    except ValueError:
        print("Not an integer... aborting")
        exit()
    if (choice < 1 or choice > valid_range ):
        print("Invalid selection... aborting")
        exit()
    else:
        optout = input("Are you sure to apply the action to " + clients[choice][1] + "? (Y/n): ")
        if ( optout == "Y" ):
            return choice
        else:
            print("Cancelled by user")
            exit()

def getConClients(action):
    if (action == 'add' ):
        if (os.path.isfile(args.csvfile)):
            with open(args.csvfile) as csv_file:
                i=0
                clientDict={ }
                csv_reader = csv.DictReader(csv_file, delimiter=';')
                for row in csv_reader:
                    i+=1
                    clientDict.update({ i: [ row['name'], row['ip'] ] })
                return clientDict
        else:
            print("No CSV File found... exiting")
            exit()
    else:
        return getBannedIPs()

def Menu(action):
    clientDict = getConClients(action)
    if ( clientDict ):
        print("Select entry to <" + action + ">:")
        for x in clientDict:
            print( str(x) + ": " + clientDict[x][0] + " (" + clientDict[x][1] + ")" )
        auswahl = selection(clientDict)
        clientAction(clientDict[auswahl][1], action)
    else:
        print("No entries found... exiting")
        exit()

if __name__ == "__main__":
    class color:
        UNDERLINE = '\033[4m'
        END = '\033[0m'
    parser = argparse.ArgumentParser(description="This script uses nftables to ban clients from patched Jamulus servers.\nGet the patched server @ " + color.UNDERLINE + "https://github.com/dingodoppelt/jamulus/tree/logging" + color.END + "\nmake sure nftables is installed and has a basic ruleset loaded to which you can add your JamulusBans set.\n\n" + color.UNDERLINE + "example for creating a basic nftables configuration:" + color.END + "\n\t\"sudo nft add table firewall\"\n\t\"sudo nft add chain firewall input\"\n\t\"sudo nft add set firewall JamulusBans { type ipv4_addr\\; size 1024\\; flags timeout\\; }\"\n\t\"sudo nft add rule firewall input ip saddr @JamulusBans drop\"", formatter_class=RawTextHelpFormatter)
    parser.add_argument("--timeout", "-t", default='2h', help="set the default bantime, e.g. 30m, 1d... (default: 2h)")
    parser.add_argument("--csvfile", "-f", default='/tmp/JamulusClients.csv', help="set path to the csvfile generated by the Jamulus server (default: /tmp/JamulusClients.csv)")
    parser.add_argument("--banset", "-s", default="ip firewall JamulusBans", help="set the name of the set to be used for the nftables blacklist (default: ip firewall JamulusBans)")
    parser.add_argument("--unban", "-u", action='store_true', help="select addresses to unban from the server")
    parser.add_argument("--unbanAll", action='store_true', help="unban all currently banned clients")
    args = parser.parse_args()
    if args.unbanAll:
        print("Unbanning all currently banned clients...")
        unbanAll(getBannedIPs())
        exit()
    if args.unban:
        Menu('delete')
        exit()
    Menu('add')
    exit()
