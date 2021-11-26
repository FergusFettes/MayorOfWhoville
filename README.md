# The Daily Life of the Mayor of Whoville!

Welcome to the small region of Wholand, where the mayor has a very busy schedule visiting all the townships in their district!

For this you need docker. And nothing else of course, such is the beauty of docker. Oh, actually you might need docker-compose too.

Ah and to hear the audio you need to install the requirements with 

`pip install -r extern_requirements.txt`

To start with, build the images with
`docker build -t whoville .`

## Docker-compose version:
Run `docker-compose up`

and you will see the activities of the townships in the district of Whoville! Oh frabjous day!

## Docker Swarm version, for real heros:
To start the Center for Mayoral Activities (which coordinates the movements of the mayor, as well as sending and recieving donations), run

`docker service create --replicas 1 --name cma --network=host whoville:latest ./cma_start.sh`

if that all starts nicely, get the townships running and connecting to the server with

`docker service create --replicas 10 --name town --network=host whoville:latest ./town_start.sh`

now you can see what is up in the district! Either run

`docker service logs -f cma`

to see the activity in the Center for Mayoral Activities or

`docker service logs -f town`

to see what is going on in the towns.

If you want to calm the activity down a little run 

`docker service scale town=3`

to remove some towns. Unfortunately, sometimes the mayor gets lost in the process (if they were in one of the towns that was removed) but they will get resurrected.

## Suspicious?

If you are suspicious that nothing is actually happening, please run 

`python3 host_listener.py`

to hear a direct broadcast from the mayor, wherever they are! They will also tell you where they are at the moment.

Enjoy!
