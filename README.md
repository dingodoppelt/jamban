# jamban
This script works in conjunction with a patched Jamulus server (https:/dingodoppelt/jamulus/tree/logging)
and nftables to kickban users by IP.

included example configurations for nftables:

\#1:  (sudo nft -f ex1-ruleset.nft)
```
flush ruleset
add     table   ip       jamban
add     chain   jamban   input          { type filter hook input priority 0 ; policy accept; }
add     set     jamban   banset         { type ipv4_addr; flags timeout; size 4096; }
add     rule    jamban   input          ip saddr @banset counter drop
```
\#2:  (sudo nft -f ex2-ruleset.nft)
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

CAUTION: the example configurations overwrite existing rulesets for nftables

see "jamban.py --help" for more information
