# Contributing

## Makefile targets

A number of default make targets are provided.  You can run `make help` to get a short summary of each.

Useful targets:
  * `make check`: runs `yapf` and `pylint` to check formatting and code correctness.  A `.pylintrc` is  provided with some defaults to make it a little less picky.
  * `make docs` : build documentation in HTML and Markdown.  By default, it will automatically generate API documentation for everyting in `myproject`.  Output documents can be found in `docs/build`.
  * `make clean`: cleans up generated binaries, virtualenvs, and documentation

## Coding style and correctness

This repo provides some default targets and configuration for `yapf` and `pylint`.

### yapf
`yapf` is used to ensure everyone on a project is using a consistent format that complies with the PEP8 formatting recommendations that are standard within the Python community.  You can check your code's format:
```
make check-format
```
and even reformat automatically:
```
make format
````

`yapf.ini` is used to configure various rules.  The main customization we have in ours to is allow lines to be
120 characters long, vs. the more standard (but too narrow) 80 characters.

### pylint
[`pylint`](http://www.pylint.org) is used to check code for common errors, as well as other common recommendations from PEP8.  It's a great tool to run even while you're still developing code - it can help catch "gotchas" before you ever run into the bugs!  When you run it, it will provide you a list of the errors in your code, as well as a score.  Your goal is a 10/10.  To run it:
```
make pylint
```

## Auto-generated documentation

With proper docstrings, this repo can be used to automatically generate SDK/API documentation in a variety of formats.  It uses [Sphinx](https://www.sphinx-doc.org/en/master/),  and [sphinx-autoapi](https://sphinx-autoapi.readthedocs.io/en/latest/) to parse `autoapi_dirs` given in `docs/source/conf.py`.   Some example docstrings:

    """ My module that does something """


    class class1(object):
        """
        This is a class that is a class
        """
        def classfunc1(self, arg1, arg2):
            """Is a class function
            Parameters:
            arg1 (int): an integer argument
            arg2 (str): a string argument
    
            Returns:
            str: A concatenation of arg1 and arg2
            """

            return str(arg1) + " " + arg2


    def func1(arg1=0, arg2=0):
        """ This is a function that is a function
        Parameters:
        arg1 (int): an integer argument
        arg2 (int): a second integer argument
        Returns:
        str: the sum of the arguments
        """

        return arg1 + arg2