# Building Lumigator with Pants

[Pants](https://www.pantsbuild.org/) is a polyglot build system for monorepos. It uses a combination of special
files (`BUILD`, or `BUILD.pants` in this repo) to denote meta instructions about what types of code you have and
how you'd like it to be packaged, published, tested, etc. It 'knows' how to then build and deliver your code
as native packaging formats, e.g., a python wheel, pex, zip/tar bundle, etc.

The benefits here are achieved over time as a system adds more services, meta-code, and more. Pants 'knows' what each system depends on
and will ensure that if a target has an implicit dep on another target, e.g., package `A` depends on `B`, but `B` depends on `C, & Z`, that packages `C, Z, B` and then `A`
will be built. It handles 3rd-party dependencies and has support for packaging software into containers.

# Important bits to know
At a high level, this is how Pants' important / special files work together.

note - `//<file>` is shorthand for the root of this repo, likely `<lumigator directory>/<file>`.

- `//.pants.bootstrap` - special file that is executed by pants *prior* to everything else. used to inject specific env vars or handle
special cases, mostly related to linux/macos and cuda/noncuda setup that pants can't be informed about otherwise.
- `//pants.toml` - main configuration file for pants options.
- `//pants_ci.toml` - config file with a small number of overrides that is used in our github actions.
- `//BUILD.pants` - special BUILD file to define Environments, root-level macros, and defaults.
- `//pants-plugins/**` - plugin/macros for pants that _we_ own.

The following files are less specific to pants but useful to know about.

- `Makefile` - sets some specific Make targets for convenience, including developer environment setup and provides a simple alias for CI targets.
- `//3rdparty/python` - location of 3rd-party python dependencies for the entire repo. This can change, though it's easier to make everything
work with a common set of external deps. Will cover more in a distinct section.
- `//lumigator/` - main location of code directly related to the Lumigator platform - e.g., application code.
- `.github/` - github actions

So when you run a command like: `pants run <some-docker-target>`, pants (at a high level) does the following:

- runs `.pants.bootstrap` to pre-populate the rest of the processes it starts
- reads `pants.toml/pants_ci.toml` and `BUILD.pants` to sort out Environments and basic settings. Note that args on the CLI will override settings in these files.
- determines deps for the target
- determine if it needs to build anything to make the deps available
- builds things in a sandboxed env without access to your current shell process
- if builds succeed, finish and put outputs where they belong.



## Handling 3rd-party deps

We (and many others) have a special issue with Torch. Torch has several version specifiers and pypi indexes for its variations -
e.g., Cuda is not required to run torch, but if it uses Cuda, it'll pull in many nvidia cuda wheels as dependencies. Problem is,
it's sorta hard to differentiate between `Linux with CUDA` and `Linux without CUDA` in normal python setuptools syntax, and there's basicaly `macos`, `linux_cpu`, and `linux_gpu`
targets for torch.

This is handled in Lumigator by having pants manually override the dependency on Torch in `3rdparty/python/BUILD` and making judicious use of Parametrizations,
including a special Macro that makes some annoyances with this a bit easier to use.

There's some weird bits in how this is done.



## Parametrization

parametrization is a way of using pants to build across platforms. many targets can take a `parametrize` argument, which effectively is a macro
that makes *multiple* targets that each define some set of params.


`//BUILD.pants` and `//pants-plugins/parametrize_platforms.py` contain the logic for handling parametrization for cross-platform dep management.
, as well as a custom `crossplatform_pex` target that correctly maps the platform deps to the right generated pex target so you don't have to.

For the most part, if you want to run something _locally_ and not via compose or helm, please use either:

- explicit parametrization if needed:
--  `pants test <target>@parametrize=darwin`
- wrapper script:
--  `./pants.sh test <target>`

the wrapper script will attempt to parametrize for you, and will report errors if it doesn't think the target you want is parametrizable.
