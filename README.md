# TIPICO SERVER: Test Inutile per Provare Inutilmente pliCO

This is just a simplified example of a typical HW controlling application

## Installation

### Installing
From the wheel

```
pip tipico_server-XXX.whl
```

from Source

```
pip install .
```

During development you want to use

```
pip install -e .
```

that install a python egg with symlinks to the source directory in such 
a way that chages in the python code are immediately available without 
the need for re-installing (beware of conf/calib files!)

### Uninstall

```
pip uninstall tipico_server
```

### Config files

The application uses `appdirs` to locate configurations, calibrations 
and log folders: the path varies as it is OS specific. 
The configuration files are copied when the application is first used
from their original location in the python package to the final
destination, where they are supposed to be modified by the user.
The application never touches an installed file (no delete, no overwriting)

To query the system for config file location, in a python shell:

```
import tipico_server
tipico_server.defaultConfigFilePath
```


The user can specify customized conf/calib/log file path for both
servers and client (how? ask!)


## Usage

### Starting Servers

Starts the 2 servers that control one device each.

```
tipico_start
```


### Using client 

See tipico


### Stopping Tipico

To kill the servers run

```
tipico_stop
```

More hard:

```
tipico_kill_all
```



## Administration Tool

For developers.


### Testing

Never commit before tests are OK!
To run the unittest and integration test suite executipicoTipico source dir

```
python setup.py test
```


### Creating a Conda environment

See plico

### Packaging and distributing

See https://packaging.python.org/tutorials/distributing-packages/#

To make a source distribution

```
python setup.py sdist
```

and the tar.gz is created in tipico/dist


If it is pure Python and works on 2 and 3 you can make a universal wheel 

```
python setup.py bdist_wheel --universal
```

Otherwise do a pure wheel

```
python setup.py bdist_wheel
```

The wheels are created in tipico/dist. I suppose one can delete 
tipico/build now and distribute the files in tipico/dist


To upload on pip (but do you really want to make it public?)

```
twine upload dist/*
```