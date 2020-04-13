#!/bin/sh

vmanage show device status

vmanage show device config

vmanage show templates

vmanage show policies list

vmanage show policies definition

vmanage show policies local

vmanage show policies central

vmanage import templates --file tests/vmanage-templates.yml

vmanage import policies --file tests/vmanage-policies.yml

vmanage export templates --file /tmp/vmanage-templates-cli.yml

vmanage export policies --file /tmp/vmanage-policies-cli.yml

vmanage certificate push