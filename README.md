# ECIR-MeSH-Suggest-Demo

## Use of UMLS and MetaMAP:

To use umls or metamap method for suggestion, it requires building of elastic server for both methods. For UMLS, please follow instruction on [umls_link](https://github.com/ielab/elastic-umls); for MetaMAP, follow instruction on [metamap_link](https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/documentation/Installation.html)


## Preparation
Download our fine-tuned model from [model_link](https://drive.google.com/drive/folders/1VF5yeYgHnFtaspWGZNAsUIp-kQyHUzsI?usp=sharing)

Then put model insiede library as:
```
model/checkpoint-80000

model/PubMed-w2v.bin
```


## Useful commands for Enviroment Setup:

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


## To start/initialise

To start server, go to server directory, then run:

`python3 main.py`

To start client, go to web-app directory, then run:

`npm start`

## Citing

If you use the *Mesh Suggester* system in your research, please cite the following paper:

```bibtex
@inproceedings{wang2023mesh,
  title={Mesh Suggester: A Library and System for Mesh Term Suggestion for Systematic Review Boolean Query Construction},
  author={Wang, Shuai and Li, Hang and Zuccon, Guido},
  booktitle={Proceedings of the Sixteenth ACM International Conference on Web Search and Data Mining},
  pages={1176--1179},
  year={2023}
}
```

## License

Shield: [![CC BY-NC-ND 4.0][cc-by-nc-nd-shield]][cc-by-nc-nd]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-NoDerivs 4.0 International License][cc-by-nc-nd].

[![CC BY-NC-ND 4.0][cc-by-nc-nd-image]][cc-by-nc-nd]

[cc-by-nc-nd]: http://creativecommons.org/licenses/by-nc-nd/4.0/
[cc-by-nc-nd-image]: https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png
[cc-by-nc-nd-shield]: https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg


[![License: CC BY-NC-ND 4.0](https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png)](https://creativecommons.org/licenses/by-nc-nd/4.0/)





