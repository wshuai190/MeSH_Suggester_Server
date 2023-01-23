# ECIR-MeSH-Suggest-Demo


Useful commands:

`conda create --prefix ./envs python==3.8`

`conda activate ./envs`

`pip install -r requirement.txt`


`conda install -c conda-forge nodejs`

`conda upgrade -c conda-forge nodejs`


If your conda does not have git, install git:

`conda install -c anaconda git`

Clone tevatron under the root directory:

`git clone https://github.com/texttron/tevatron`

`cd tevatron`

`pip3 install --editable .`

Go to `web-app` directory, then:

`npm install`

To start server, go to server directory, then run:

`python3 main.py`

To start client, go to web-app directory, then run:

`npm start`

During server start, call:

`prepare_model()` to load model, etc in ram, this function can also be load if current server fail to reload model
`prepare_model will output mesh_dict, model, tokenizer, retriever, look_up, model_w2v`

During client time:

Post Method Input:

`{"Keywords": list[str], "Type":str()}`

Type can be "Semantic", "Fragment", or "Atomic"


Post Method Output:

`list[{"Keywords": list[str], "Type":str(), "MeSH_Terms": list[str]}]`

Method to call 

`suggest_mesh_terms(input_dict={Post Method Input}, model, tokenizer, retriever, look_up, mesh_dict, model_w2v)`

Method return Post Method Output


