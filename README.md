# jamban
This script works in conjunction with a [patched Jamulus server](https:/dingodoppelt/jamulus/tree/logging)
and [nftables](https://www.nftables.org/) to kickban users by IP.

## requirements
1. start the Jamulus server with the rpc server enabled. Run "Jamulus --help" for more infos
2. configure nftables to contain a table, chain and set visible to jamban (see "jamban.py --help" for defaults or below for examples)
#
- output of "jamban.py --help":
```
usage: jamban [-h] [--timeout [TIMEOUT]] [--banset BANSET] [--unban] [--unbanAll] [--kickListeners] [--kickNoNames] [--list] [--listRaw] [--environmentfile [ENVIRONMENTFILE]]

This script uses nftables to ban clients from patched Jamulus servers.
Get the patched server @ https://github.com/dingodoppelt/jamulus/tree/release

        Make sure nftables is installed and has a basic ruleset loaded to which you can add your banset.
        See the included example configurations for nftables (ex*-ruleset.nft)

options:
  -h, --help            show this help message and exit
  --timeout, -t [TIMEOUT]
                        set the default bantime, e.g. 30m, 1d, etc. or leave blank for permban (default: 2h)
  --banset, -s BANSET   set the name of the set to be used for the nftables blacklist (default: ip jamban banset)
  --unban, -u           select addresses to unban from the server
  --unbanAll            unban all currently banned clients
  --kickListeners, -L   kick all current listeners
  --kickNoNames, -N     kick all clients named No Name
  --list, -l            list clients as metadata input to icecast
  --listRaw, -r         list raw client details
  --environmentfile, -f [ENVIRONMENTFILE]
                        path to a systemd environment file containing JSONRPCPORT and JSONRPCSECRETFILE variables
```
#
- included example configurations for nftables:

1:  (sudo nft -f ex1-ruleset.nft)
```
add     table   ip       jamban
add     chain   jamban   input          { type filter hook input priority -1; policy accept; }
add     set     jamban   banset         { type ipv4_addr; flags timeout; size 4096; }
add     rule    jamban   input          ip saddr @banset counter drop
```
2:  (sudo nft -f ex2-ruleset.nft)
```
table ip jamban {
        set banset {
                type ipv4_addr
                size 4096
                flags timeout
        }

        chain input {
                type filter hook input priority -1; policy accept;
                ip saddr @banset counter drop
        }
}
```

- CAUTION: the example configurations *can* break existing rulesets for nftables.
