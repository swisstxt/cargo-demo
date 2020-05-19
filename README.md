# Cargo Demo

In this tutorial, you will get an introduction to the Cargo Cluster and its properties.
You will create an deploy an application to get used to Cargo.
The cargo cluster that is used is named ```cargo-demo``` with its FQDN ```cargo-demo.cargo.stxt.media.int``` so
make sure to change the name whenever you find this name in the tutorial. 
You need the following installed and working on your local computer:
- Python3 with Pip
- kubectl >= 1.15
- git
- docker
- Connection to the Cargo Cluster (e.g you should be able to successfully execute kubectl get namespaces)


## Preparations

The Python Application in this tutorial is a simple Python Flask application. Flask is a Webframework
that makes it easy to publish Content on a website with Python. With just a few lines of Python code we
can create a simple website for demonstration purpose.  
To follow the tutorial and to be able to execute all the commands, the first thing we want to do is 
clone the repository from github. 

```bash
TODO: git clone git@github.com:swisstxt/cargo-live-demo.git
```

Change to the checked out directory and create a virtual environment with it's dependencies:
```bash
python3 -m venv venv
source venv/bin/activates
pip install -r requirements.txt
```

You are ready to run the application locally. So lets try that out:

```bash
python app.py
```

Open the address [http://127.0.0.1:8088] in a web browser. You can see
a website with a greetings page, your hostname and the actual time.
The visits counter is not working at the moment, will implement this later.
Let's have a quick look at what is happening here. There is basically just on file that gets executed,
app.py. The part you can see than on your website is:

```html
<h3>Hello {name}!</h3>
<b>Hostname:</b> {hostname}<br/>
<b>Actual time:</b> {t_now}<br/>
<b>Visits:</b> {visits}<br/>
```
- Line one will print Hello + an environment variable (name)
- Line two will gather your hostname and show it
- Line three will print the actual time in a human readable format
- Line four will show how many visits where already on that website (not working at the moment). 

Open the file app.py to get some more insight - the comments in there describe what is done. It is a simple
app with less than 50 lines of code and half of it are comments - but don't worry if you don't understand it
completely. Let's just say this is an application that shows some html lines. 


## Docker Container

The application works, but let's put it into a Docker container. 
First we need to find a base Docker Image from which we can build the program. The most-common way is to search on
[Docker Hub](https://hub.docker.com/_/python?tab=tags) for an official Docker Image.
In this case this we want to use a Python Image. We need to select which tag to use.
Normally you have tags for different versions and systems.
For instance for python version 3.8 we have multiple tags:
- 3.8-slim
- 3.8-buster
- 3.8-alpine
- ...

These tags differ in it's substruction and characteristics.
Because we don't need a "full" operating system and want to keep it small, we choose _3.8-slim_.
This image is really small in size (only around 60 MB) and provides already everything we need. 
But basically, you can pick whatever tags suits you best.


### Dockerfile

Next step is to write a Dockerfile. Create a file with the name "Dockerfile" an pur first line into it:
```bash
FROM python:3.8-slim
```

This line says that we will use the already existing python:3.8-slim image as builder image.
In the next line, we will set the working directory for ```COPY```, ```RUN``` and ```CMD```, which we are
going to use later on, to /app. 
If the WORKDIR doesn’t exist in the container, it will be created which will be the case in our example. 
```bash
WORKDIR /app
```

We copy the application and the requirements contents into the container at /app
```bash
COPY app.py requirements.txt /app/
```

The next step is to create a virtual environment inside the /app directory. This is done via the ```RUN``` command.
```bash
RUN python -m venv venv
```

Now that Python is ready, let's install the required dependencies to run the application, that is Flask and redis.
The dependencies are inside the requirements.txt file that we copied before.  
```bash
RUN /app/venv/bin/pip install -r requirements.txt
```

To be able to communicate with the application, a port must be enabled. So we make port 8088 available to
the world outside this container
```bash
EXPOSE 8088
```

Our docker image is nearly complete. When you opened the website before, you saw a greeting line on top.
This greeting value writes "Hello" + a name that is defined in an environment variable. Choose whatever you 
want to see on top of the page, e.g your name.
```bash
ENV NAME World
```

The last step is to run the application itself as soon as the container starts.
This can be achieved with the ```CMD``` instruction. 
```bash
CMD ["/app/venv/bin/python", "app.py"]
```

The dockerfile is ready now. So let's build it:
```bash
docker build . -t swisstxt/cargo-demo:latest
```

- The "." is responsible to build the file named "Dockerfile" in your directory.
- With "-t" you set a tag. It is of the format repository:version
- ":latest" is - as the name implies - always the most recent version

We want to see now if everything worked. You should see something similar as below when executing ```docker images```.
```bash
$ docker images
REPOSITORY                      TAG        IMAGE ID       CREATED         SIZE
docker.swisstxt.ch/cargo-demo   latest     dadf63bfb3cd   4 seconds ago   218 MB
```

Lets try to run this container to see if everything works:
```bash
docker run -p 7070:8088 cargo-demo:latest
```

With ```-p 7070:8088``` you can map the port 7070 to the port used inside the container. 
You can now access the website on your local computer via http://127.0.0.1:7070/.

As a last step, we are going to push the newly created container to a docker hub.
There are multiple providers or you can even have a self hosted docker registry.
We are using docker.swisstxt.ch here. If you have already a login to a docker registry,
you can upload your dockerfile there - or you can just use our example for the coming chapters and skip this part. 
```bash
docker push docker.swisstxt.ch/cargo-demo:latest
```

###Recap

In this chapter, we executed the application app.py and executed it to see if everything works as. We then
put this Application inside a Docker container to run it as microservice. 

The Dockerfile we created has only a few lines:
```bash
FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt app.py /app/
RUN python -m venv venv
RUN /app/venv/bin/pip install -r requirements.txt
EXPOSE 8088
ENV NAME World
CMD ["/app/venv/bin/python", "app.py"]
```


## Kubernetes Deployment

The docker container is running locally, alright, but now we want to put it on the cargo cluster. We then will be
able to use features like scaling, monitoring and so on. 


## Namespace

We want to put our recently created container in it's own namespace. But what is a namespace?  
Kubernetes supports multiple virtual clusters backed by the same physical cluster. These virtual clusters
are called namespaces. Think of it as a virtual cluster in the cluster. Some namespace characteristics:
- Names of resources need to be unique within a namespace
- Namespace cannot be nested
- Each resource can only be in one namespace

Change to the directory "tutorial1" and have look at the file "1-namespace.yml". 
We create a new namespace now: 
```
kubectl create -f 1-namespace.yml
```

Execute these commands to examine the newly created namespace:
```
kubectl get namespaces --show-labels
kubectl get namespaces cargo-demo --show-labels
```
You can see that this namespaces was created just some seconds ago, right? You also see the labels that were defined.
Change to this newly created namespace with
```
kubectl config set-context --current --namespace=cargo-demo
```

or even easier, use 
```
kubens cargo-demo
```
if you have ```kubens``` installed. If not, check it out here: https://github.com/ahmetb/kubectx


## Deployment

Let's continue with a deployment. 
A Deployment provides declarative updates for Pods and ReplicaSets. So it describes Pods
and ReplicaSets at once. A Deployment can create and destroy Pods dynamically.
Apply the second file "2-deployment.yml" to the cluster.  

```
kubectl create -f 2-deployment.yml
```

We created a deployment and a replicaset. Let's look at them:
```
kubectl get deployments -o wide
kubectl get replicasets -o wide
```

The Pod was also created
```
kubectl get pods -o wide
```

We have one deplyoment, one replicaset with one POD running right now. Make sure that the STATUS is really
running.
The ```-o wide``` shows some extended information. 


## Service
Ok, the Pod is running, but we are not able to access it right now. That's where a Service comes in. 
A Service is a way to expose an application running on a set of Pods as a network service.
Kubernetes gives Pods their own IP addresses and a single DNS name for a set of Pods, and can load-balance across them.
Each Pod gets its own IP address, however in a Deployment, the set of Pods running in one moment in time could be
different from the set of Pods running that application a moment later.
If some Pods (backends) provides functionality to other Pods (frontends), how do the frontends find out and keep
track of which IP address to connect to, so that the frontend can use the backend part of the workload? Thats task is up
to the service.

Create a service with:
```
kubectl create -f 3-service.yml
```

And now have a look at it:
```
kubectl get services -o wide
```

## Ingress

Finally, we create an Ingress.
Ingress is an API object that manages external access to the services in a cluster, typically HTTP.
Ingress exposes HTTP and HTTPS routes from outside the cluster to services within the cluster.
Traffic routing is controlled by rules defined on the Ingress resource. You can see Ingress as directly connected
to a Service. Cargo is using NGINX as Ingress Controller.
Attention! Before executing the next command, make sure you set the host to your actual Cargo Cluster name! 
```
kubectl create -f 4-ingress.yml
```

To see if the ingress was successfully created, execute
```
kubectl get ingress
```

Our service is ready and running now. Open your webbrowser at https://cargo-demo.cargo-demo.cargo.stxt.media.int. If 
everything worked, you should see the same website as before when executing the app locally or in a docker container.  

## Cleanup
