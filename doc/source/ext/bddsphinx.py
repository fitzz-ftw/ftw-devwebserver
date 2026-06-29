"""
BDD Gherkin Extension for Sphinx.

This module provides directives and roles to structure BDD-style documentation
(Given, When, Then) and integrate executable code steps.
"""

import sys

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.directives.code import CodeBlock
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

# Initialize the logger
logger = logging.getLogger(__name__)

# Registry to track IDs across the build process
_id_registry = set()


def validate_id(node_id, docname, lineno):
    """Check for duplicate IDs and emit a warning if found."""
    if node_id in _id_registry:
        logger.warning(
            f"Duplicate BDD ID found: '{node_id}' in {docname}:{lineno}", location=(docname, lineno)
        )
    else:
        _id_registry.add(node_id)

def bdd_role(name, 
             rawtext, 
             text, 
             lineno, 
             inliner, 
             options=None, 
             content=None)  -> tuple[list, list]:   # noqa: F821
    """
    Parse BDD-style roles from reStructuredText.

    This function transforms a role like :given:`Text <target> &&:class:c1::id:i1`
    into a docutils node. It supports custom CSS classes and unique IDs.

    :param name: The name of the role (feature, scenario, given, etc.).
    :param rawtext: The original text as written in the rst file.
    :param text: The content inside the role markers.
    :param lineno: The line number in the source file.
    :param inliner: The docutils inliner object.
    :param options: Options provided to the role.
    :param content: Additional content for the role.
    :return: A list containing a docutils node and a list of system messages.
    """
    # Separate the main content from the attribute block using the '&&:' separator
    if content is None:
        content = []
    if options is None:
        options = {}
    if "&&:" in text:
        main_part, attr_part = text.split("&&:", 1)
    else:
        main_part, attr_part = text, ""

    # print(f"{main_part=}, {attr_part=}, {text=}, {rawtext=}")

    # Extract link target if format is "Label <target>"
    label, target = (main_part.strip(), None)
    if "<" in main_part and main_part.endswith(">"):
        label, target = main_part[:-1].split("<")
        label, target = label.strip(), target.strip()

    # Initialize nodes with the base BDD class
    classes = [f"bdd-{name}", "bdd-role"]
    node_id = None

    # Split attributes by '::' and parse key:value pairs
    attrs = attr_part.split("::")
    for attr in attrs:
        if not attr:
            continue

        # Split key and value by ':'
        if ":" in attr:
            key, val = attr.split(":", 1)
            key = key.strip()
            val = val.strip()

            # Apply class names or set the ID
            if key == "class":
                classes.extend(val.split(","))
            elif key == "id":
                node_id = val
                # Validate ID uniqueness
                validate_id(node_id, inliner.document.settings.env.docname, lineno)

    # Configure node arguments
    node_args = {"classes": classes}
    if node_id:
        node_args["ids"] = [node_id]

    # Return a reference node (link) if a target is found, otherwise an inline node
    if target and "/" in target in target:
        node = nodes.reference(rawtext, label, refuri=target, **node_args)
    elif target:
        node = nodes.reference(rawtext, label, refid=target, **node_args)
    else:
        node = nodes.inline(rawtext, label, **node_args)

    return [node], []


class BDDDirective(Directive):
    """
    Directive to create BDD containers (feature, scenario, given, when, then, step).
    Supports optional :class: and :id: attributes.
    """

    # Hier definierst du, dass die Direktive GENAU EIN Argument erwartet
    # required_arguments = 1
    # Damit das Argument nicht als Teil des Inhalts interpretiert wird
    # final_argument_whitespace = True

    has_content = True
    option_spec = {
        "class": directives.class_option,
        "id": directives.unchanged,
    }

    def run(self):
        # Determine classes
        classes = [f"bdd-{self.name}", "bdd-directive"] + self.options.get("class", [])

        # Create container
        container = nodes.container(classes=classes)

        # Set ID for the container (serves as anchor for :ref:)
        # Check if ID exists and validate uniqueness
        if "id" in self.options:
            node_id = self.options["id"]
            # validate_id(node_id, self.env.docname, self.lineno)  # type: ignore
            container["ids"].append(node_id)
            container["names"].append(node_id)
            self.state.document.note_explicit_target(container)
        self.state.nested_parse(self.content, self.content_offset, container)
        if container.parent:
            print(f"Debug: {container.parent.children=}", file=sys.stderr)
        return [container]


class HBDDDirective(SphinxDirective):
    """
    Directive to create BDD containers (feature, scenario, given, when, then, step).
    Supports optional :class: and :id: attributes.
    """
    # Hier definierst du, dass die Direktive GENAU EIN Argument erwartet
    required_arguments = 1
    # Damit das Argument nicht als Teil des Inhalts interpretiert wird
    final_argument_whitespace = True

    has_content = True
    option_spec = {
        "class": directives.class_option,
        "id": directives.unchanged,
    }

    def run(self):
        # Access the document context
        doc = self.state.document
        parent_feature = doc.attributes.get('last_feature')

        # Determine classes
        classes = [f"bdd-{self.name}", "bdd-directive"] + self.options.get("class", [])

        # Create container
        section = nodes.section(classes=classes)
        title_node = nodes.title(text=self.arguments[0])
        section += title_node

        # Set ID for the container (serves as anchor for :ref:)
        # Check if ID exists and validate uniqueness
        if "id" in self.options:
            node_id = self.options["id"]
            validate_id(node_id, self.env.docname, self.lineno) # type: ignore
            section["ids"].append(node_id)
        else:
            section["ids"].append(nodes.make_id(self.arguments[0].replace(" ", "-")))

        if self.name=="feature":
            doc["last_feature"] = section
            
        elif self.name == "scenario" and parent_feature:
            parent_feature.setup_child(section)
            # print(f"Debug: {section}=", file=sys.stderr)
            # return[]

        self.state.nested_parse(self.content, self.content_offset, section)

        return [section]

class StepDirective(CodeBlock):
    """
    Specialized directive for code steps, inheriting from Sphinx CodeBlock.

    Supports auto-numbering of steps and manual counter reset.

    Allows embedding executable code with full syntax highlighting
    and support for :id: and :class: attributes.
    """
    
    # Add BDD-specific options
    option_spec = CodeBlock.option_spec.copy()
    option_spec.update(
        {
            "id": directives.unchanged,
            "class": directives.class_option,
            "resetcounter": directives.flag,  # New option to reset the step counter
        }
    )

    def run(self):
        """Execute standard CodeBlock parsing and wrap result in a container."""

        # 1. Initialize counter in the environment if it doesn't exist,
        # or reset counter if the option is provided
        if not hasattr(self.env, "bdd_step_counter") or "resetcounter" in self.options:
            self.env.bdd_step_counter = 0 # type: ignore

        # 2. Increment and get the current step number
        self.env.bdd_step_counter += 1 # type: ignore
        step_number = self.env.bdd_step_counter # type: ignore

        # 3. Process the code block through the parent CodeBlock directive
        result = super().run()

        # 4. Modify the resulting node or embed it into a container
        # Since CodeBlock returns a literal_block, we wrap it in a 
        # container to apply the ID and BDD classes.  
        classes = ["bdd-step"] + self.options.get("class", [])
        container = nodes.container(classes=classes)

        # 6. Add a visual label for the step
        label = nodes.paragraph(text=f"Step {step_number}")
        label["classes"].append("bdd-step-label")
        container += label

        # 6. Check if ID exists and validate uniqueness
        if "id" in self.options:
            node_id = self.options["id"]
            validate_id(node_id, self.env.docname, self.lineno)
            container["ids"].append(node_id)

        container.extend(result)
        return [container]
