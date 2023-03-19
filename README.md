# Lego Sorter Server

## Temporary repository, enhancement of [Lego Sorter Server](https://github.com/LegoSorter/LegoSorterServer)

Lego Sorter Server provides methods for detecting and classifying Lego bricks.

## Project setup

1. Clone the repository
    ```commandline
    git clone https://github.com/czpmk/LegoSorterServerLW.git
    ```

2. Download the latest network models for detecting lego bricks from:
    ```commandline
    https://github.com/LegoSorter/LegoSorterServer/releases
    ```
   If using the following lines, please make sure the versions are correct:
    ```commandline
    wget https://github.com/LegoSorter/LegoSorterServer/releases/download/1.2.0/detection_models.zip
    wget https://github.com/LegoSorter/LegoSorterServer/releases/download/1.2.0/classification_models.zip
    ```
   Place the downloaded archives in the project's root directory. Unzip the models with the following command:
    ```commandline
    python unzip_models.py
    ```
   or extract the models manually to the directories:
    * detection_models.zip -> ./lego_sorter_server/analysis/detection/models
    * classification_models.zip -> ./lego_sorter_server/analysis/classification/models

3. Prepare environment.
   #### It's recommended to use conda virtual environment.
    * Conda environment:
        * Select, download and install a version fitting the OS and python version from:
           ```commandline
           https://docs.conda.io/en/latest/miniconda.html
           ```
        * Navigate to the repository location and create new environment with command:
          ```commandline
          conda env create -f environment.yml
          ```

    * Without conda environment:
        * Navigate to the repository location and run the following command
           ```commandline
           pip3 install -r ./requirements.txt
           ```

## How to run

In order to operate properly the server requires an **App** to receive the requests and **controllers** to manage the
LEGO bricks. By default, the server listens on port *50051*

#### If running the server in a conda environment, activate the environment:

  ```commandline
  conda activate LegoSorterServerLW
  ```

### Launch the server as a module, without exporting PYTHONPATH:

  ```commandline
  python -m lego_sorter_server
  ```

#### or skip the module (requires exporting PYTHONPATH each shell session):

  ```commandline
  export PYTHONPATH=$PYTHONPATH:.
  python lego_sorter_server
  ```

If an exception regarding the protobuf package version occurs when launching the server, downgrade protobuf version:

  ```commandline
  pip3 install protobuf==3.20
  ```

### Basic options:

* **-c, --brick_category_config** - json file with brick-category mapping specification. REQUIRED if using the server in
  sorting mode.
* **-f, --save_brick_images_to_file** [Flag] - save cropped images (bricks only) to file.
* **-r, --reset_state_on_stop** [Flag] - remove current state on each Stop Sorting call from app.
* **-l, --queue_size_limit** - Limit the number of items in detection and classification queues
  (Asynchronous Sorter only!). Discards all new items while max queue items are achieved.
  Accepted range = [0, 100], where 0 means limit disabled. Default = 0 (disabled).
* **--detection_worker** - Selected DETECTION worker mode (Asynchronous Sorter only!). Options: [Thread, Process].
  Default = 'Thread'.
* **--classification_worker** - Selected CLASSIFICATION worker mode (Asynchronous Sorter only!).
  Options: [Thread, Process]. Default = 'Thread'.

### Test mode options:

Test mode is meant for debug only. It runs the server without the need to connect the app by feeding the server with
images provided in directory 'tester_images'. Test options can be provided by the following arguments:

* **--test_mode** [Flag] - Enable test mode.

#### The following options are to be discarded if test mode is not enabled.

* **-o, --test_operation** - Test operation. Options: [AsyncSorter, SyncSorter]. Default 'AsyncSorter'.
* **-t, --test_time** - Test time [seconds]. Default 60s.
* **-d, --capture_delay** - Capture delay [milliseconds]. Default 500ms.

## Lego Sorter App

To test **Lego Sorter Server**, use the [Lego Sorter App](https://github.com/czpmk/LegoSorterAppLW), which is an
application dedicated for this project.

[Original Lego Sorter App](https://github.com/LegoSorter/LegoSorterApp)

## How to send a request (Optional)

**Lego Sorter Server** uses [gRPC](https://grpc.io/) to handle requests, the list of available methods is defined
in `LegoSorterServer/lego_sorter_server/proto/LegoBrick.proto`.\
To call a method with your own client, look
at [gRPC documentation](https://grpc.io/docs/languages/python/basics/#calling-service-methods)

