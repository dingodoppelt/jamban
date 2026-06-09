#!/usr/bin/python3
import csv
import subprocess
import os
import re
import argparse
import sys
from argparse import RawTextHelpFormatter
import socket
import json

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

def kickListeners(confFile):
    args.timeout = '60s'
    listeners = getClients('add', confFile)
    for x in listeners:
        if (listeners[x][2] == 'Listener'):
            clientAction( extract_ip(listeners[x][1]), 'add')

def kickNoNames(confFile):
    args.timeout = '60s'
    listeners = getClients('add', confFile)
    for x in listeners:
        if (listeners[x][0] == 'No Name'):
            clientAction( extract_ip(listeners[x][1]), 'add')

def listClients(confFile):
    metadata = ''
    clients = getClientsFromRPC(confFile)
    for x in clients :
        if Instruments(clients[x][4]) != "Streamer" and Instruments(clients[x][4]) != "Recorder" :
            if clients[x][0] != "" :
                metadata += clients[x][0]
            if Instruments(clients[x][4]) != "-" :
                metadata += "(" + Instruments(clients[x][4]) + ")"
            if clients[x][3] != "-" :
                metadata += "+from+" + clients[x][3].replace("United Kingdom", "UK").replace("United States","USA")
            metadata += ",+"
    metadata = ' '.join(metadata.split()).replace(" ","+")
    if metadata == "" :
        metadata = "waiting+for+musicians....."
    print(metadata[:len(metadata) - 2])

def listRawClients(confFile):
    clients = getClientsFromRPC(confFile)
    print(json.dumps(clients))

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

def getConfig(confFile):
    __config__ = {}
    if confFile:
        try:
            with open(confFile, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                    try:
                        key, value = line.strip().split('=')
                        if key == 'JSONRPCSECRETFILE':
                            __config__['rpcSecretFilePath'] = value
                        elif key == 'JSONRPCPORT':
                            __config__['rpcPort'] = int(value)
                    except ValueError:
                        continue
        except FileNotFoundError:
            print(f"environment file {confFile} not found.")
    else:
        __location__ = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(__location__, 'config.json')) as json_config_file:
            __config__ = json.load(json_config_file)
    return __config__

def getClientsFromRPC(confFile):
    config = getConfig(confFile)
    rpcHost = "localhost"
    rpcPort = config['rpcPort']
    rpcSecretFilePath = config['rpcSecretFilePath']
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if (os.path.isfile(rpcSecretFilePath)):
            with open(rpcSecretFilePath) as secret:
                secret = secret.read()
                s.connect((rpcHost, rpcPort))
                authRequest = bytes('{"id":"Auth","jsonrpc":"2.0","method":"jamulus/apiAuth","params":{"secret": "' + secret.rstrip() + '"}}\n', encoding='utf-8')
                s.sendall(authRequest)
                ackn = s.recv(1024).decode('utf-8')
                if (ackn == '{"id":"Auth","jsonrpc":"2.0","result":"ok"}\n'):
                    s.sendall(b'{"id":"Clients","jsonrpc":"2.0","method":"jamulusserver/getClients","params":{}}\n')
                    dictParsed = json.loads(s.recv(16384))['result']['clients']
                    clientDict={}
                    i=1
                    for client in dictParsed:
                        clientDict.update({ i: [ client['name'], client['address'], client['city'], client['countryName'], client['instrumentCode'], client['id'], client['skillLevelCode'] ] })
                        i+=1
                    return clientDict
        else:
            print("No CSV File found... exiting")

def getClients(action, config):
    if (action == 'add' ):
        return getClientsFromRPC(config)
    else:
        return getBannedIPs()

def drawMenu(clientDict):
    for x in clientDict:
            print((color.BOLD + "  {0:>2}: {1}" + color.END + " ({2})").format(str(x), clientDict[x][0], extract_ip(clientDict[x][1])))

def menu(action, config):
    clientDict = getClients(action, config)
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
            optout = input("Are you sure to apply the action <" + action + "> to " + color.BOLD + extract_ip(clientDict[choice][1]) + color.END + "? (Y/n): ")
            if ( optout == 'Y' ):
                clientAction( extract_ip(clientDict[choice][1]), action)
            else:
                print("Cancelled by user")
                exit()
    else:
        print("No entries found... exiting")

def extract_ip(address):
    ipv6_pattern = r'\[([^\]]+)\](?::\d+)?'
    ipv4_pattern = r'([^\[]+?)(?::\d+)?$'

    ipv6_match = re.match(ipv6_pattern, address)
    if ipv6_match:
        return ipv6_match.group(1)

    ipv4_match = re.match(ipv4_pattern, address)
    if ipv4_match:
        return ipv4_match.group(1).split(':')[0]

SkillLevels = [
    "",
    "Beginner",
    "Intermediate",
    "Expert"
]

Instruments = [
    "None",               # 0
    "Drum Set",           # 1
    "Djembe",             # 2
    "Electric Guitar",    # 3
    "Acoustic Guitar",    # 4
    "Bass Guitar",        # 5
    "Keyboard",           # 6
    "Synthesizer",        # 7
    "Grand Piano",        # 8
    "Accordion",          # 9
    "Vocal",              # 10
    "Microphone",         # 11
    "Harmonica",          # 12
    "Trumpet",            # 13
    "Trombone",           # 14
    "French Horn",        # 15
    "Tuba",               # 16
    "Saxophone",          # 17
    "Clarinet",           # 18
    "Flute",              # 19
    "Violin",             # 20
    "Cello",              # 21
    "Double Bass",        # 22
    "Recorder",           # 23
    "Streamer",           # 24
    "Listener",           # 25
    "Guitar+Vocal",       # 26
    "Keyboard+Vocal",     # 27
    "Bodhran",            # 28
    "Bassoon",            # 29
    "Oboe",               # 30
    "Harp",               # 31
    "Viola",              # 32
    "Congas",             # 33
    "Bongo",              # 34
    "Vocal Bass",         # 35
    "Vocal Tenor",        # 36
    "Vocal Alto",         # 37
    "Vocal Soprano",      # 38
    "Banjo",              # 39
    "Mandolin",           # 40
    "Ukulele",            # 41
    "Bass Ukulele",       # 42
    "Vocal Baritone",     # 43
    "Vocal Lead",         # 44
    "Mountain Dulcimer",  # 45
    "Scratching",         # 46
    "Rapping",            # 47
    "Vibraphone",         # 48
    "Conductor"           # 49
]

if __name__ == "__main__":
    class color:
        GREEN = '\033[92m'
        RED = '\033[91m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        END = '\033[0m'
    parser = argparse.ArgumentParser(description="This script uses nftables to ban clients from patched Jamulus servers.\nGet the patched server @ " + color.UNDERLINE + "https://github.com/dingodoppelt/jamulus/tree/release" + color.END + "\n\n\tMake sure nftables is installed and has a basic ruleset loaded to which you can add your banset.\n\tSee the included example configurations for nftables (ex*-ruleset.nft)", formatter_class=RawTextHelpFormatter)
    parser.add_argument("--timeout", "-t", nargs='?', const='permban', default='2h', help="set the default bantime, e.g. 30m, 1d, etc. or leave blank for permban (default: 2h)")
    parser.add_argument("--banset", "-s", default="ip jamban banset", help="set the name of the set to be used for the nftables blacklist (default: ip jamban banset)")
    parser.add_argument("--unban", "-u", action='store_true', help="select addresses to unban from the server")
    parser.add_argument("--unbanAll", action='store_true', help="unban all currently banned clients")
    parser.add_argument("--kickListeners", "-L", action='store_true', help="kick all current listeners")
    parser.add_argument("--kickNoNames", "-N", action='store_true', help="kick all clients named No Name")
    parser.add_argument("--list", "-l", action='store_true', help="list clients as metadata input to icecast")
    parser.add_argument("--listRaw", "-r", action='store_true', help="list raw client details")
    parser.add_argument("--environmentfile", "-f", nargs='?', default=None, help="path to a systemd environment file containing JSONRPCPORT and JSONRPCSECRETFILE variables")
    args = parser.parse_args()
    if args.unbanAll:
        print("Unbanning all currently banned clients...")
        unbanAll(getBannedIPs())
    elif args.unban:
        menu('delete', None)
    elif args.kickListeners:
        kickListeners(args.environmentfile)
    elif args.kickNoNames:
        kickNoNames(args.environmentfile)
    elif args.list:
        listClients(args.environmentfile)
    elif args.listRaw:
        listRawClients(args.environmentfile)
    else:
        menu('add', args.environmentfile)
