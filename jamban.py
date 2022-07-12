#!/usr/bin/python3
import csv
import subprocess
import os
import re
import argparse
import sys
from argparse import RawTextHelpFormatter

def getTimeOut(action):
    timeOut = ''
    if (action == 'add') and (args.timeout != 'permban'):
        timeOut = " timeout " + args.timeout
    return timeOut

def clientAction(client, action):
    cmd = "sudo nft " + action + " element " + args.banset + " { " + client + getTimeOut(action) + " }"
    if not subprocess.call(cmd, shell=True):
        print(color.GREEN + "[SUCCESS]: " + color.END + args.banset + ": " + action + " element " + color.BOLD + client + color.END)

def unbanAll(clients):
    for IP in clients:
        clientAction(clients[IP][1], 'delete')

def kickListeners():
    args.timeout = '60s'
    listeners = getClients('add')
    for x in listeners:
        if (listeners[x][2] == 'Listener'):
            clientAction(listeners[x][1], 'add')

def listClients():
    metadata = ''
    clients = getCSVFile()
    for x in clients :
        if clients[x][4] != "Streamer" and clients[x][4] != "Recorder" :
            if clients[x][0] != "" :
                metadata += clients[x][0]
            if clients[x][4] != "-" :
                metadata += "(" + clients[x][4] + ")"
            if clients[x][3] != "-" :
                metadata += "+from+" + clients[x][3].replace("United Kingdom", "UK").replace("United States","USA")
            metadata += ",+"
    metadata = ' '.join(metadata.split()).replace(" ","+")
    if metadata == "" :
        metadata = "waiting+for+musicians....."
    print(metadata[:len(metadata) - 2])
    
def getBannedIPs():
    i=0
    clientDict={}
    cmd = "sudo nft list set " + args.banset
    cmdOutput = subprocess.check_output(cmd, shell=True)
    IPs = re.findall(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b', str(cmdOutput))
    for x in IPs:
        i+=1
        clientDict.update({ i: [ '', x ] })
    return clientDict

def getCSVFile():
    if (os.path.isfile(args.csvfile)):
        with open(args.csvfile) as csv_file:
            i=0
            clientDict={}
            csv_reader = csv.DictReader(csv_file, delimiter=';')
            for row in csv_reader:
                i+=1
                clientDict.update({ i: [ row['name'], row['ip'], row['city'], row['country'], row['instrument'], row['instrumentPicture'], row['skill'] ] })
            return clientDict
    else:
        print("No CSV File found... exiting")

def getClients(action):
    if (action == 'add' ):
        return getCSVFile()
    else:
        return getBannedIPs()

def drawMenu(clientDict):
    for x in clientDict:
            print((color.BOLD + "  {0:>2}: {1}" + color.END + " ({2})").format(str(x), clientDict[x][0], clientDict[x][1]))

def menu(action):
    clientDict = getClients(action)
    if ( clientDict ):
        print("Select entry to <" + action + ">:\n")
        drawMenu(clientDict)
        try:
            choice = int(input("\nSelect entry " + color.BOLD + "(1 - " + str(len(clientDict)) + ")" + color.END + " or any other character to abort: "))
        except ValueError:
            print("Not an integer... aborting")
            exit()
        if choice not in range(1, len(clientDict) + 1):
            print("Invalid selection... aborting")
        else:
            optout = input("Are you sure to apply the action <" + action + "> to " + color.BOLD + clientDict[choice][1] + color.END + "? (Y/n): ")
            if ( optout == 'Y' ):
                clientAction(clientDict[choice][1], action)
            else:
                print("Cancelled by user")
                exit()
    else:
        print("No entries found... exiting")

if __name__ == "__main__":
    class color:
        GREEN = '\033[92m'
        RED = '\033[91m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        END = '\033[0m'
    parser = argparse.ArgumentParser(description="This script uses nftables to ban clients from patched Jamulus servers.\nGet the patched server @ " + color.UNDERLINE + "https://github.com/dingodoppelt/jamulus/tree/logging" + color.END + "\n\n\tMake sure nftables is installed and has a basic ruleset loaded to which you can add your banset.\n\tSee the included example configurations for nftables (ex*-ruleset.nft)", formatter_class=RawTextHelpFormatter)
    parser.add_argument("--timeout", "-t", nargs='?', const='permban', default='2h', help="set the default bantime, e.g. 30m, 1d, etc. or leave blank for permban (default: 2h)")
    parser.add_argument("--banset", "-s", default="ip jamban banset", help="set the name of the set to be used for the nftables blacklist (default: ip jamban banset)")
    parser.add_argument("--unban", "-u", action='store_true', help="select addresses to unban from the server")
    parser.add_argument("--unbanAll", action='store_true', help="unban all currently banned clients")
    parser.add_argument("--kickListeners", "-L", action='store_true', help="kick all current listeners")
    parser.add_argument("--list", "-l", action='store_true', help="list clients as metadata input to icecast")
    args = parser.parse_args()
    if args.unbanAll:
        print("Unbanning all currently banned clients...")
        unbanAll(getBannedIPs())
    elif args.unban:
        menu('delete')
    elif args.kickListeners:
        kickListeners()
    elif args.list:
        listClients()
    else:
        menu('add')
