# Insight DevOps Engineering Systems Puzzle

## Table of Contents
1. [Introduction](README.md#introduction)
2. [Approach](README.md#approach)
3. [General Notes](README.md#general-notes)
4. [Listen port in conf.d/flaskapp.conf set at 80 and “The web address is set at localhost:8080, changed to 80”](README.md#Listen-port-in-conf.d/flaskapp.conf-set-at-80-and-“The-web-address-is-set-at-localhost:8080,-changed-to-80)
5. [Theexpose port in the Dockerfile for flask is set at 5001](README.md#The-expose-port-in-the-Dockerfile-for-flask-is-set-at-5001)
6. [proxy_set_header Host parameter is configured to be $host](README.md#proxy_set-header-Host-parameter-is-configured-to-be-$host)
7. [Conclusion](README.md#conclusion)


# Introduction 
([Taken from https://github.com/InsightDataScience/systems-puzzle](https://github.com/InsightDataScience/systems-puzzle))
Imagine you're on an engineering team that is building an eCommerce site where users can buy and sell items (similar to Etsy or eBay). One of the developers on your team has put together a very simple prototype for a system that writes and reads to a database. The developer is using Postgres for the backend database, the Python Flask framework as an application server, and nginx as a web server. All of this is developed with the Docker Engine, and put together with Docker Compose.

Unfortunately, the developer is new to many of these tools, and is having a number of issues. The developer needs your help debugging the system and getting it to work properly.

# Approach
For this problem i've identified the following bugs and the following changes (in the sequence i figured these out):
* Listen port in `conf.d/flaskapp.conf` set at 80, changed to 8080 and "The web address is set at localhost:8080, changed to 80"
* The expose port in the `Dockerfile` for flask is set at 5001, changed to 5000 and proxy_pass is set at `conf.d/flaskapp.conf` was set at proxy_pass http://flaskapp:5001 changed to http://flaskapp:5000
* proxy_set_header Host parameter is configured to be $host, change to $host:$proxy
#### Bonus:
* Added `tables.py`, added flask-table in `requirements.txt`, `templates/success.html` and added on `app.py` for success function.

## General notes:
For this problem, i was mostly unfamiliar with middle-tier related configuration and technologies with only a passing working knowledge and some experience handling Docker containers. In each problem that will be illustrated in the following section weren't possible without the guidance of some references which i will list down. For starters, despite having a docker in my system, i haven't installed `docker-compose` until when i tried running the the dockers provided in the original set of instructions. I applied a test-driven, fail fast approach to this problem to take advantage of error logging and fault tolerance measures placed in these systems. In practice however, i would be more cautious especially when handling production critical infrastructure or just work on a sandbox replication of the production system or dev/test environment first. With all these said, let me talk about how i encountered and approached each bug mentioned.

### Listen port in conf.d/flaskapp.conf set at 80 and "The web address is set at localhost:8080, changed to 80"
After my first attempt in running the set of instructions provided in the instructions, (actually it was more insightful when i tried running docker-compose itself rather than the original set of commands), as expected i would get cannot connect as per instruction.
![cannot connect](https://raw.githubusercontent.com/jinalklaulitz/Insight_DevOps_challenge/master/port8080_localhostcantbereached.png)
I noticed the Nginx was running yet i'm getting errors with regards to the , so intuitive this would a configuration error with regards to connectivity. 
![container status](https://raw.githubusercontent.com/jinalklaulitz/Insight_DevOps_challenge/master/container_status.png)
I check `docker-compose.yml` and noticed the following setting:
```docker
 nginx:
    image: "nginx:1.13.5"
    ports:
      - "80:8080"
    volumes:
      - ./conf.d:/etc/nginx/conf.d
    networks:
      - web_network
    depends_on: 
      - flaskapp
```
Ports was set to 80:8080. Following Bastian Haase's explanation of [this](https://youtu.be/Xn8k8n2NU30), it means that incoming connections would go through port 80 then redirected to 8080 of the container, which is the expected port for the web server to listen on. Based on `conf.d/flaskapp.conf`, Nginx's listening port is set at 80. I have an option to either choose to change the `docker-compose.yml`'s ports setting' or `conf.d/flaskapp.conf`, i choose to do the latter. Looking back the former would have less impact, considering i ended up changing the web address port to 80 as well. Atleast now i can access nginx, although i still have no access to the flask application.
![bad gateway](https://raw.githubusercontent.com/jinalklaulitz/Insight_DevOps_challenge/master/bad_gateway.png)

### The expose port in the Dockerfile for flask is set at 5001
I stumbled upon the idea that flask's port setting is at 5000 while reviewing the docker container logs.
![Port 5000](https://raw.githubusercontent.com/jinalklaulitz/Insight_DevOps_challenge/master/port_5000.png)
I confirmed while upon reading the documentation that is the [default port](http://flask.pocoo.org/docs/1.0/api/) setting. So i wonder what was the port setting for Flask, and since it was building built through the `Dockerfile`, i would check this out.

```
FROM python:3

ENV PYTHONUNBUFFERED 1
RUN mkdir -p /opt/services/flaskapp/src
COPY requirements.txt /opt/services/flaskapp/src/
WORKDIR /opt/services/flaskapp/src
RUN pip install -r requirements.txt
COPY . /opt/services/flaskapp/src
EXPOSE 5001

CMD ["python", "app.py"]
```
According to a blog post regarding [EXPOSE](https://we-are.bookmyshow.com/understanding-expose-in-dockerfile-266938b6a33d), it mentions that 
>The EXPOSE instruction exposes the specified port and makes it available only for inter-container communication. Let’s >understand this with the help of an example.
>
>Let’s say we have two containers, a nodejs application and a redis server. Our node app needs to communicate with the redis server for several reasons.
>
>For the node app to be able to talk to the redis server, the redis container needs to expose the port. Have a look at >the Dockerfile of official redis image and you will see a line saying EXPOSE 6379. This is what helps the two >containers to communicate with each other.
>>So when your nodejs app container tries to connect to the 6379 port of the redis container, the EXPOSE instruction is what makes this possible.

Since the EXPOSE port of the server is at 5001 but it is reachable through 5000 given what was being displayed by the logs, and `docker-compose.yml` has it's network settings correctly configured. I simply changed the port from 5001 to 5000 in the `Dockerfile`. I also noticed that proxy_pass was set similarly in `conf.d/flaskapp.conf` with a value of http://flaskapp:5001, and i changed it to http://flaskapp:5000 to be consistent as this the address used to communicate to access the Flask App server. This results to allowing me to access the `index.html`. 
![accessible index.html](https://raw.githubusercontent.com/jinalklaulitz/Insight_DevOps_challenge/master/indexhtml.png)

### proxy_set_header Host parameter is configured to be $host
In the following section, admittedly this where i got stuck for awhile with a simple problem with an obvious solution (retrospectically speaking) however i found myself going through checking a number of options, even so far as to modify the success function in `app.py`, thinking the issue lies there. The **TL;DR** version of the story is that i tried to test out if adding new items work, it didn't and later on i noticed something was wrong with the redirected url after clicking submit, namely it would show up as ```localhost%2Clocalhost/success```. After much testing of various components, it eventually became clear to me it was an issue with Nginx configuration and after reading a stackoverflow post, i noticed i had to declare the port in the proxy_set_header host from $host to $host:$port in the `conf.d/flaskapp.conf` file. I believe that it's important i provide a narrative on the investigation process i went through chasing wrong leads as a number of problems encounter like, from experience, tend only to come from actually going through them. But i think i provide a reasonable process for me to eventually find the true problem.
#### long version

After successfully gaining access to the index.html file, i would try to test out if submitting something with valid values on the form would work, as a way to check up if there is a connection between Flask and the Postgres. After pressing submit, i would encounter the following:
![success error](https://raw.githubusercontent.com/jinalklaulitz/Insight_DevOps_challenge/master/success_error.png)
Unfortunately, instead of immediately thinking that the error was something related to the web server, my mindset was that i haven't tested of out if the connection between the appserver and the backend is working. So instead i went on the verify if indeed when i click on submit, the new entries would enter into the table in the Postgre server. To do so, i went on to interactively access the docker container `db` and open up psql and tried to check if my initial testing did went through. it did.
![items query](https://raw.githubusercontent.com/jinalklaulitz/Insight_DevOps_challenge/master/items_query.png)
From there it was clear to me the connection between the two is working well enough, but i had apprehensions that possibly that it's possible place files but not read them. I continued on by going through the `app.py` since i remembered about the strange url format and Flask would make use of `@app.route` to redirect pages. I took on Bastian Haase's lead to understand `render_template` and `@app.route`, since i understood the problem as an "output-ing" problem rather than what it actually is. I ended up changing the success function based on [examples](http://www.blog.pythonlibrary.org/2017/12/14/flask-101-adding-editing-and-displaying-data/)
i saw online. This lead to adding `tables.py`, adding flask-table in `requirements.txt`, `templates/success.html`, modifiying `app.py` for success function then rebuilt the images of the containers. This didn't solve the problem as i originally expected. So out of the whim i wrote down `localhost/success` and this popped out:
![flask tables](https://raw.githubusercontent.com/jinalklaulitz/Insight_DevOps_challenge/master/flasktables.png)
The actual page is working! Then i asked myself what other things can affect the url address? That's when it became clear to me that Nginx was possibly causing this the current problem i was attempting to solve. So i checked online and noticed this post from [stack overflow](https://stackoverflow.com/questions/41348714/flasknginxgunicorn-redirect-error) and tested it and finally went to the web address i expected it to go.

# Conclusion
Since i'm able to access the main page of the webpage and perform adding of items in the database and verify by redirecting me to a page that shows the Items table. I think that at the bare minimum, i was able to accomplish this puzzle given the limited amount of time i was given to work with this problem and limited skillset i got with these technologies except for Docker, which i already some working experience with. All in all, i think i did learn something new going through this challenge about how systems interact especially in an environment that encapsulates other "virtual environments". Although, if i had more time, it would be good to perform some form of testing or adding in some fault tolerance measures to improve the reliability of these systems. 
