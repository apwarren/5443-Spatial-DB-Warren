from comms import CommsListener

# example game user
#creds = {
#    "exchange": "battleship",
#    "port": "5672",
#    "host": "battleshipgame.fun",
#    "user": "us_navy",
#    "password": "rockpaperscissorsrabbitdonkey",
#    "hash": "61ec12b68d0ded5f6a84b7d1f6d4d8e70695c2ba5dd7176fc3e4c3d53db9ecf2",
#}
creds = {
     "id": 15,
     "name": "kraken",
     "regdate": 1669156402,
     "exchange": "battleship",
     "port": 5672,
     "host": "battleshipgame.fun",
     "password": "kX3aF8x5z0Sw",
     "hash": "32223921880817397656263709201856725525"
 }
print("Comms Listener starting. To exit press CTRL+C ...")
# create instance of the listener class and sending in the creds
# object as kwargs
commsListener = CommsListener(**creds)

# tell rabbitMQ which 'topics' you want to listen to. In this case anything
# with the team name in it (user) and the broadcast keyword.
commsListener.bindKeysToQueue([f"#.{creds['name']}.#", "#.broadcast.#"])

# now really start listening
commsListener.startConsuming()