# File System Layout
Use a file system hierarchy for all the things - lean on redundancy for now (e.g. create extra subfolders) to allow for potential expansion

```
my-public-keys/
|--- current-hash.md
|--- keys/
|    |--- current.md
|    |--- old.md
|--- sigchain/
|    |--- tip.md
|    |--- 0.md
|    |--- 1.md
|    |--- ...
|    |--- n.md
|--- proofs/
|    |--- summary.md
|    |--- github.md
|    |--- twitter.md
|    |--- hacker-news.md
|    |--- ...
|    |--- randomsite.md
|--- messages/
|--- ?????
|--- teams/
|--- ????
```
