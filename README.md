# ConfigParity

ConfigParity is used to interpret and translate configurations and configuration data
using a similar methodology to how Django or other ORMs create and manage data relationships.
However, Config Parity builds those relationships out of Pythonic objects, not a database.
Once those objects are created, they can be manipulated and exported to any of the many
ways it can receive the data.

### Installation/Development Installation
Future plans are to make this library available via Artifactory.
In the mean time, you can help develop this application by installing a development
environment:

1. clone this repository
2. `cd configparity`
3. `python3 -m virtualenv .` or similar virtualenv setup
4. `source bin/activate`

### Usage/Example:
Config Parity does not connect to any devices or APIs itself. It is a module that is imported
into other tools that manage that data connection process. Included in this project is a
samples folder, with config files that can be used to experiment and test code with.

Start by hopping into your preferred Python interactive shell tool (such as iPython or
Junyper Notebook). The first thing we need to do is import the `ASA` model.

```
from configparity.models.cisco.asa import ASA
```

Next, let's load a sample configuration from a file and parse it into a string:

```
sample = "samples/cisco/asa/5508_9.8.config"
sample_file = open(sample, "r")```
config = "\n".join(sample_file.readlines())
```

Then, we can build an instance of the ASA mode, into the `asa` variable. This next line
builds the instance from a configuration string, but you can also use `from_dict` with a dict
instead of a configuration string. Example:

```
asa = ASA(from_config=config)
```

Interaction with the `asa` instance is done through the same methods you traverse data in 
Python lists, tuples, and dicts. For example:

```
asa.hostname
```
or

```
asa.interface[3].vlan
```

The `asa` instance is using a `ASA` model class, with many class attributes declared under a
type-control system built into Config Parity as field classes. `asa.hostname` is a StrField
and `asa.interface` is a ListField that only allows the ModelField for the `Interface` model.

Underneath the objects, you can see the related instances by using:

```
asa.values
```

If you want to manipulate the data, you set the value for the "variable" just like in typical
Python notation:

```
asa.hostname = "Firewall"
```

Now, if you check `asa.hostname`, it returns the new value "Firewall", as expected. But what
good is this if you cannot export your change? Try this:

```
print(asa.config)
```

If you do not need the entire configuration, then try this:

```
print(asa.only_changes)
```

Maybe you don't need configuration at all? How about a pure Pythonic dict?

```
asa.dictionary
```

Want to serve up this data to something else that may not be written in Python?

```
asa.json
```

### How to contribute
Instead of writing your custom configuration parser for whatever tooling or automation you
are doing, write the parsing and generating into Config Parity, on the foundation included
that simplifies the process. Then, import Config Parity into your project, and have it do
the heavy lifting on how your code interacts with configurations.

[Apache 2.0 License Information](https://www.apache.org/licenses/LICENSE-2.0.txt)
