# Lego Sorter Server - (LW - lightweight)

## Temporary copy of repository - (TODO: remove after fork is made)

https://github.com/LegoSorter/LegoSorterServer

Lego Sorter Server provides methods for detecting and classifying Lego bricks.

## How to run

1. Download the repository

```commandline
git clone https://github.com/LegoSorter/LegoSorterServer.git
```

2. Install python packages:
```commandline
pip3 install -r ./requirements.txt
```

4. Download network models for detecting lego bricks (NOPE! Just paste the links to the browser and paste the files to
   the project's root catalogue)

```commandline
wget https://github.com/LegoSorter/LegoSorterServer/releases/download/1.2.0/detection_models.zip
wget https://github.com/LegoSorter/LegoSorterServer/releases/download/1.2.0/classification_models.zip
```

3. Set access (run the command in the project root directory)

```commandline
sudo chmod -R 777 .
```

5. Extract models (there is a script for that: "unzip_models.py")

```commandline
unzip detection_models.zip -d ./LegoSorterServer/lego_sorter_server/analysis/detection/models
unzip classification_models.zip -d ./LegoSorterServer/lego_sorter_server/analysis/classification/models
```
OR use the script
```commandline
python3 unzip_models.py
```

4. Go to the root directory

```commandline
cd LegoSorterServer
```

5. Export *PYTHONPATH* environmental variable

```commandline
export PYTHONPATH=.
```
OR
```commandline
python3 set_pythonpath.py
```

6. Run the server

```commandline
python lego_sorter_server
```

The server is now ready to handle requests. By default, the server listens on port *50051*

## Lego Sorter App

To test **Lego Sorter Server**, use the [Lego Sorter App](https://github.com/LegoSorter/LegoSorterApp), which is an
application dedicated for this project.

## How to send a request (Optional)

**Lego Sorter Server** uses [gRPC](https://grpc.io/) to handle requests, the list of available methods is defined
in `LegoSorterServer/lego_sorter_server/proto/LegoBrick.proto`.\
To call a method with your own client, look
at [gRPC documentation](https://grpc.io/docs/languages/python/basics/#calling-service-methods)

