# The Daily Life of the Mayor of Whoville!

Welcome to the small region of Wholand, where the mayor has a very busy schedule visiting all the townships in their district!

For this you need docker. And nothing else of course, such is the beauty of docker.

To start with, build the images with
`docker build -t whoville .`

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
