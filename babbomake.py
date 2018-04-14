#!/usr/bin/env python3.5

import importlib.util
import shlex
import sys
from subprocess import Popen


class MakeRule:
    def __init__(self, name, dependencies, commands, phony=False):
        self.name = name
        self.dependencies = dependencies
        self.commands = commands
        self.phony = phony
    
    def rule_string(self):
        result = ''
        if self.phony:
            result += '.PHONY: {}\n'.format(self.name)
        dependency_string = ' '
        for dependency in self.dependencies:
            dependency_string += '{} '.format(dependency)
        result += '{}: {}\n'.format(self.name, dependency_string[1:])
        for command in self.commands:
            result += '\t{}\n'.format(command)
        return result


def make_traversal(rule_dict):
    rule_to_rule_deps = {}
    for rule, kws in rule_dict.items():
        rule_to_rule_deps[rule] = set()
        for dependency in kws['dependencies']:
            if dependency in rule_dict:  # If there is a rule to make the dependency:
                if dependency == rule:
                rule_to_rule_deps[rule].add(dependency)
        for rule_dependency in rule_to_rule_deps[rule]:
            if rule_dependency == rule:
                raise ValueError('Rule "{}" depends on itself'.format(rule))
    result = []
    while rule_to_rule_deps:
        no_dependency_rules = [rule for rule in rule_to_rule_deps if rule_to_rule_deps[rule]]
        for rule in no_dependency_rules:
            result.append(rule)
            rule_to_rule_deps.remove(rule)
    return result        


def makefile_string(rule_dict):
    rules = {rule: MakeRule(rule, **kwargs).rule_string() for rule, kwargs in rule_dict.item()}
    order = make_traversal(rule_dict)
    ordered_rules = []
    for rule in order:
        ordered_rules.append(rules[rule])
    return '\n'.join(ordered_rule.rule_string() for ordered_rule in ordered_rules)


def main(input_file_name, output_file_name):
    spec = importlib.util.spec_from_file_location('rules_module', input_file_name)
    rules_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rules_module)
    rule_dict = rules_module.rules()
    result = makefile_string(rule_dict)
    with open(output_file_name, 'w') as file_obj:
        file_obj.write(result)


if __name__ == '__main__':
    main(*sys.argv[1:])
