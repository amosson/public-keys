[![Tests](https://github.com/<your-username>/hypermodern-python/workflows/Tests/badge.svg)](https://github.com/<your-username>/hypermodern-python/actions?workflow=Tests)

# public-keys
As a young programmer, I thought PGP was interentesting, if not for communications (none of my friends could ever be bothered - this was a differnet time), then for keeping files safe on my local machines.  Of course, like many, this quickly became operationally difficult as I could never remember PGP "Passphrase".

Along came keybase.io, and I could *safely* store a PGP key in the cloud and use it on any of my devices.  Cool.  keybase.io evolved to add some interesting (albiet *controversial* features.  But like many interesing companies, [they were bought](https://keybase.io/blog/keybase-joins-zoom) and as announcement mentiones, the team is moving immediately on to Zoom.com priorities.  This isn't typically a good sign for the health of a product and as keybase.io has a reliance on a central server their service may be at long term risk.

This set of circumstances had me asking the question "How much of keybase's functionality can I implement with out relying on a **new** central service?"

Of the services that keybase provides - here are the ones that I'd like to replicate (in rough order of priority):
 * Secure storage of an encryption key across multiple devices
 * Public validation that key (and devices) belong to *an individual*
   * striclty speaking that we can validate that the key belongs to a set of public accounts on the internet
 * Asynchronous Messaging between *individuals*
 * Secure filesystems
 * Teams
 * Others
   * Account search
   * Chat between people who have never chatted before
   * [Coin Tossing](https://keybase.io/blog/cryptographic-coin-flipping)
   * [Sending messages to people who don't yet have a key](https://keybase.io/blog/crypto)

My theory / arguement goes something like this
 * Keybase's premise regarding key verification was that people have public identies and that if one tied a keybase user to the public services one could trust the keybase identity
    * This was to get get around a key shortcomming in the PGP circle-of-trust archtiecture
 * I assert that the keybase servers are redundant - if you know one public identity you can find and validate them all - no need for a central source of truth
 * There are free public services that can act as a central service for our purposes - some of these are also associted with well-known identies
    * Github, Dropbox, etc.  
    * If one were afraid of these services going out of business one could store the applicable data on multiple services
 * I also assert that the security of any crypto system should only depend on the strength / protection of the secret key and therefor we can publically publish any encrypted data we want
    * however for corporate appliations, where corporate IT departments might want belts and suspsenders, we can use protected accounts on these public providers
 * Therefore we can
   * We can publish our sigchain on any public storage provider
   * We can create a store and forward mechanism by posting messages on a public storage platform

 * Anonymity might be difficult
