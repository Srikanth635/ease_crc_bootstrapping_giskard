# RASA Actions
RASA based application for extracting useful and required information from a Natural Language Instruction.

## Steps (to run in Docker)
1. ```bash
   git clone git@github.com:Srikanth635/RASA_Actions.git
   ```
   to build the image using Dockerfile or run
   ```bash
   docker pull srikanth635/rasaactions
   ```
   to pull already built image from docker hub.
2. If cloned git repo, build Docker image by running the command
   ```bash
   docker build --tag srikanth635/rasaactions . 
   ```
2. Once the image is available, start the container using the command
   ```bash
   docker run -p 5005:5005 srikanth635/rasaactions
3. Above command takes some time to start a RASA server.
4. Once the server is up and running, open new terminal/CMD prompt and enter
   ```bash
   docker exec -it CONTAINER_ID_OR_NAME /bin/bash
   ```
   eg. docker exec -it 9ae1ec16f24c /bin/bash
5. An interactive terminal gets opened for the running docker container, then type
   ```bash
   python base.py
   ```
   and enter.
6. Then python script start executing and asks for NL instruction (Input), type it and enter.

**Note**
In step 2, we started the container by exposing port 5005, so we can also run 'base.py' locally.


## Steps (to run locally)
1. ```bash
   git clone git@github.com:Srikanth635/RASA_Actions.git
2. Get a working python environment (tested using Python 3.9)
3. Run
   ```bash
   pip install requirements.txt
4. Open the project files in your preferable IDE (eg. PyCharm)
5. From the ROOT directory, run the command
   ```bash
   rasa train
   ```
   and let the model train completely.
6. Once training is done, a **models** folder appears in the root directory with all trained models instances.
7. Then from the ROOT directory run the below command in the terminal.
   ```bash
   rasa run --enable-api
   ```
8. This will load recently trained model and start rasa server locally.
9. Once the RASA server is up and running, open the [base.py](./base.py) file and execute it.
10. It should then prompt 'Enter an NL Instruction', enter the instruction and press enter.

**Note**
To install spacy models, run the following commands in the terminal
```bash
python.exe -m spacy download en_core_web_trf
```
```bash
python.exe -m spacy download en_core_web_sm
```

## Examples
1. pour water into bowl
2. drizzle 2 ounces of honey on to salad
3. from small blue jar pour 10 liters of water in to brown jug
4. let 10 liters of water stream from blue jar into a pot
5. hold the large container and slowly let 1 quart of pancake batter onto the cooking pan
6. pour pancake batter from the ladle onto the cooking pan
7. squeeze some tomato sauce over the pizza
8. sprinkle some salt over the chicken breast
9. gush the stream of water into the cooking pot
10. hold the pipe and pour water on the flames
