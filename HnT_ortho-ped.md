# Tor Spiders
_(five minute hack-and-tell version)_

*[Travis Hoppe](http://thoppe.github.io/)*
----------
[https://github.com/thoppe/tor_spiders](https://github.com/thoppe/tor_spiders)

====

# The darknet
_sounds scary!_

The darknet is anything you can't traditionally "see" on the Internet.
If you can type it into your browser, it's probably not on the darknet.
====+
<br>

## Illegal?
_Can be._

Since it's a "back-alley" of the Internet you'll find all sorts 
of shady characters (ex. Silk Road, pornography, political dissidents).

====*

# Anonymity

Key feature of the darknet. Your IP isn't linked to you anymore.

### Tor (The Onion Router) 
<div style="footnote">
> ... is implemented by encryption in the application layer of a communication protocol stack, nested like the layers of an onion. Tor encrypts the data, including the destination IP address, multiple times and sends it through a virtual circuit comprising successive, randomly selected Tor relays. Each relay decrypts a layer of encryption to reveal only the next relay in the circuit in order to pass the remaining encrypted data on to it. The final relay decrypts the innermost layer of encryption and sends the original data to its destination without revealing, or even knowing, the source IP address.
</div>
====

### (hypothetically) Let's say you've been IP banned  
### making too many requests to LinkedIn's frontpage.
_funny story..._
====+
<br>



Use Tor to create a fake identify to connect and continue browsing.
Python module [stem](https://stem.torproject.org/) does all the heavy lifting.



## Can we do better?

====

## Tor Spiders
[https://github.com/thoppe/tor_spiders](https://github.com/thoppe/tor_spiders)
`pip install git+git://github.com/thoppe/tor_spiders`


Uses python's `threading` module (I know, not multiprocessing!) to create simultaneous Tor connections to spider a queue of urls.

====*

### Example
    from tor_spiders import tor_request_pool
    
    T = tor_request_pool(2)
    url = 'https://api.ipify.org?format=json'
        
    for x in range(10):
        T.put(url)
    
    for r in T:
        print r.text

### Output:
    {"ip":"176.126.252.12"}
    {"ip":"146.0.32.144"}
    {"ip":"176.126.252.12"}
    {"ip":"176.126.252.12"}
    {"ip":"176.126.252.12"}
    {"ip":"146.0.32.144"}
    {"ip":"176.126.252.12"}
    {"ip":"146.0.32.144"}
    {"ip":"146.0.32.144"}
    {"ip":"146.0.32.144"}

====

### What can you do with it?

#### Spidering
Silently spider a website without leaving trace to your real location.

#### Access control
Circumvent IP range blocks
(sometimes locations are mapped to same IP address)

#### Censorship detection 
Download a website and see if the country of origin changes it.

====

# Thanks you!

<div style="footnote">
I'm looking for a hardware hacker for a martial arts project. 
Got skills? Let's talk! *travis.hoppe @ gmail.com*
</div>