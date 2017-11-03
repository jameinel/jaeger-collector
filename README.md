# Overview

This charm is designed to maintain the Collector for Jaeger Tracing collection.
It is the bridge between the jaeger-agent subordinate charm that should run on
every machine and the storage backend (cassandra or elasticsearch) that contains
all of the actual saved data. There should also be a Jaeger-UI charm used to
visualize what is going on with all of your traces.


???
This charm provides [service][]. Add a description here of what the service
itself actually does.

Also remember to check the [icon guidelines][] so that your charm looks good
in the Juju GUI.

# Usage

Step by step instructions on using the charm:

Deploy Jaeger Collector along with a storage backend.

  juju deploy cassandra -n3
  juju deploy jaeger-collector
  juju add-relation jaeger-collector cassandra

Deploy the agent, to allow gathering information about the applications you
care about.
  juju deploy jaeger-agent
  juju add-relation jaeger-agent jaeger-collector


Deploy the actual application, and make sure the agent is running on that machine.
  juju deploy myspecialapp
  juju add-relation jaeger-agent myspecialapp


Deploy the UI to allow inspecting the traces
  juju deploy jaeger-ui
  juju add-relation jaeger-ui ???
  juju expose jaeger-ui

You can then browse to http://ip-address to configure the service.

## Scale out Usage

Jaeger documentation claims that you can run however many collectors you want.

## Known Limitations and Issues

Unknown what the limitations are, other than not everything has been written yet.

# Configuration


# Contact Information

Though this will be listed in the charm store itself don't assume a user will
know that, so include that information here:

## Upstream Project Name

  - http://jaeger.readthedocs.io/en/latest
  - https://github.com/jaegertracing/jaeger
  - ??? Upstream mailing list or contact information


[service]: http://example.com
[icon guidelines]: https://jujucharms.com/docs/stable/authors-charm-icon
