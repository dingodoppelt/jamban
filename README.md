# jamban
This script works in conjunction with a patched Jamulus server (https:/dingodoppelt/jamulus/tree/logging)
and nftables to kickban users by IP.

example configurations for nftables: (sudo nft -f ruleset.nft)

\#1:
```
flush ruleset
add     table   ip       jamban
add     chain   jamban   input          { type filter hook input priority 0 ; policy accept; }
add     set     jamban   banset         { type ipv4_addr; flags timeout; size 4096; }
add     rule    jamban   input          ip saddr @banset counter drop
```
\#2:
```
table ip jamban {
        set banset {
                type ipv4_addr
                size 4096
                flags timeout
        }

        chain input {
                type filter hook input priority filter; policy accept;
                ip saddr @banset counter drop
        }
}
```
you can save an example configuration in a file and pass it to "nft -f"

CAUTION: the example configurations overwrite existing rulesets for nftables

see "jamban.py --help" for more information
