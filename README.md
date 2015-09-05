# Record and Install that Package

: RIP foo

install foo globally and add it to your dotifle (specified in conf.yaml)

: RIP --pip foo

installs foo with pip and
- if we're in a virtual env, adds it to the requirements file of your
project,
- if not, adds it to your dotfile for pip packages.

Recommended bash alias:

: alias ripip="rip --pip"
