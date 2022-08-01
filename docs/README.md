# Verse Library Documentation
The forder contain the document template for the Verse library. The document for the library is generated using [sphinx](https://www.sphinx-doc.org/en/master/). 

## Prerequsites 
The following libraries are required for compile verse's document
- sphinx
- myst-parser 
- numpydoc 
- sphinx_rtd_theme

The required packages can be installed using command 
```
python3 -m pip install -r requirements-doc.txt
```

## Compiling The Documents
### For Linux User
For linux user, the document can be compiled using command 
```
make html
```
in the ```docs/``` folder

### For Windows User
For Windows user, the document can be compiled using command 
```
./make.bat html
```
in the ```docs/``` folder

## Viewing Compiled Documents
The compiled result can be found in ```docs/build/html``` folder. The root of the compiled document is stored in ```docs/build/html/index.html```

## Example Architectural Document
An example highlevel architectural document can be found in file ```docs/source/parser.md```

## Example Docstring for Class/Function
An example docstring for class function can be found in file ```verse/agents/base_agent.py``` for class ```BaseAgent``` and function ```BaseAgent.__init__``` and ```BaseAgent.TC_simulate```